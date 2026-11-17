// Served at /deseret-words.json for the Latin/Deseret toggle (loaded only when someone switches).
import WORDS from '../data/deseret-words.json';
export const GET = () => new Response(JSON.stringify(WORDS), { headers: { 'Content-Type': 'application/json' } });
