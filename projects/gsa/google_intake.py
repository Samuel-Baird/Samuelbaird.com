"""Read-only worker readiness checks; never authorize intake or modify config."""
import argparse
import json
from pathlib import Path
import urllib.parse
import pipeline as p
import gsa


def questions(schema):
    result = {}
    for item in schema.get('items', []):
        entries = []
        if 'questionItem' in item:
            entries.append(item['questionItem']['question'])
        entries.extend(item.get('questionGroupItem', {}).get('questions', []))
        for question in entries:
            qid = question['questionId']
            p.require(qid not in result, 'Duplicate question ID in schema')
            result[qid] = {'title': item.get('title', ''), 'question': question}
    return result


def validate_mapping(schema, mapping):
    available = questions(schema)
    p.require(mapping and set(mapping).issubset(set(gsa.FIELDS) - {'row_id'}), 'Invalid question mapping')
    p.require(set(mapping) & {'title', 'isbn', 'doi'}, 'Map a title, ISBN or DOI')
    p.require(len(set(mapping.values())) == len(mapping), 'Question mapped more than once')
    for qid in mapping.values():
        p.require(qid in available, 'Mapped question absent from Form schema')
        p.require('textQuestion' in available[qid]['question'], 'Non-text question needs explicit adapter')
    return available


def poll_freeform(db, api, config):
    """Queue unparsed requests for review, without inventing bibliographic fields."""
    from datetime import datetime, timedelta, timezone
    p.require(config.get('intake_approved') is True, 'Staff intake approval missing')
    mapping = config.get('form_question_ids', {})
    p.require(set(mapping) == {'materials', 'topics', 'quality_of_life', 'bugs'}, 'Incomplete free-text mapping')
    p.require(len(set(mapping.values())) == 4, 'Duplicate mapped question')
    db.execute('CREATE TABLE IF NOT EXISTS form_requests (form_id TEXT, response_id TEXT, answers TEXT NOT NULL, status TEXT NOT NULL DEFAULT "needs_review", PRIMARY KEY(form_id,response_id))')
    source = 'freeform:' + config['form_id']
    checkpoint = db.execute('SELECT value FROM checkpoints WHERE source=?', (source,)).fetchone()
    start = datetime.now(timezone.utc)
    params = {'pageSize': 5000}
    if checkpoint:
        since = datetime.fromisoformat(checkpoint[0].replace('Z', '+00:00')) - timedelta(minutes=5)
        params['filter'] = 'timestamp >= ' + since.isoformat().replace('+00:00', 'Z')
    rows, seen_tokens = {}, set()
    while True:
        page = api.call('GET', p.FORMS + config['form_id'] + '/responses', params=params)
        for response in page.get('responses', []):
            answers = {}
            for role, qid in mapping.items():
                values = response.get('answers', {}).get(qid, {}).get('textAnswers', {}).get('answers', [])
                p.require(len(values) <= 1, 'Multivalue response requires review')
                answers[role] = values[0]['value'] if values else ''
            rid = response['responseId']
            encoded = json.dumps(answers, sort_keys=True)
            p.require(rid not in rows or rows[rid] == encoded, 'Response changed during pagination')
            rows[rid] = encoded
        token = page.get('nextPageToken')
        if not token:
            break
        p.require(token not in seen_tokens, 'Repeated pagination token')
        seen_tokens.add(token)
        params['pageToken'] = token
    inserted = 0
    with db:
        for rid, encoded in rows.items():
            old = db.execute('SELECT answers FROM form_requests WHERE form_id=? AND response_id=?', (config['form_id'], rid)).fetchone()
            p.require(old is None or old[0] == encoded, 'Changed response requires reconciliation')
            if old is None:
                db.execute('INSERT INTO form_requests(form_id,response_id,answers) VALUES(?,?,?)', (config['form_id'], rid, encoded))
                inserted += 1
        db.execute('INSERT INTO checkpoints VALUES(?,?) ON CONFLICT(source) DO UPDATE SET value=excluded.value', (source, start.isoformat()))
    return inserted


def document_body(document, tab_id):
    pending = list(document.get('tabs', []))
    while pending:
        tab = pending.pop()
        if tab.get('tabProperties', {}).get('tabId') == tab_id:
            return tab['documentTab']['body']
        pending.extend(tab.get('childTabs', []))
    raise ValueError('Configured changelog tab not found')


def readiness(api, config):
    # Independent checks retain useful results when one resource is inaccessible.
    report = {'intake_approved': config.get('intake_approved') is True,
              'reviewers': config.get('reviewers', []), 'checks': {}}
    def check(name, operation):
        try:
            report['checks'][name] = {'ok': True, 'result': operation()}
        except Exception as exc:
            # Never serialize HTTP bodies, credential subprocess output or tokens.
            report['checks'][name] = {'ok': False, 'error_type': type(exc).__name__,
                                      'http_status': getattr(exc, 'code', None)}
    def form():
        schema = api.call('GET', p.FORMS + config['form_id'])
        result = {'questions': questions(schema), 'mapping_valid': False}
        try:
            if config.get('form_question_ids'):
                mapping = config['form_question_ids']
                p.require(set(mapping) == {'materials', 'topics', 'quality_of_life', 'bugs'}, 'Incomplete free-text mapping')
                p.require(len(set(mapping.values())) == 4, 'Duplicate mapped question')
                available = questions(schema)
                p.require(all(qid in available and 'textQuestion' in available[qid]['question'] for qid in mapping.values()), 'Free-text schema changed')
                result['mapping_type'] = 'freeform_review'
            else:
                validate_mapping(schema, config['question_map'])
            result['mapping_valid'] = True
        except ValueError as exc:
            result['mapping_error'] = str(exc)
        return result
    def index():
        base = 'https://sheets.googleapis.com/v4/spreadsheets/' + config['toc_spreadsheet_id']
        metadata = api.call('GET', base, params={'fields': 'sheets.properties'})
        p.require(any(s['properties']['title'] == config['toc_sheet_name'] for s in metadata['sheets']), 'Index tab missing')
        tab = "'" + config['toc_sheet_name'].replace("'", "''") + "'!A1:B2"
        rows = api.call('GET', base + '/values/' + urllib.parse.quote(tab, safe='')).get('values', [])
        p.require(rows and rows[0] == ['Name', 'Folder Path'], 'Index headers changed')
        return {'headers_verified': True, 'sample_rows': len(rows) - 1}
    def changelog():
        doc = api.call('GET', p.DOCS + config['changelog_document_id'], params={'includeTabsContent': 'true'})
        document_body(doc, config['changelog_tab_id'])
        return {'configured_tab_readable': True}
    check('form_schema', form)
    check('archive_index', index)
    check('changelog_tab', changelog)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    print(json.dumps(readiness(p.Google(config), config), indent=2))
