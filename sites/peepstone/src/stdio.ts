#!/usr/bin/env node
/** Local entry point: run Peepstone over stdio (Claude Desktop, Claude Code, etc.). */
import { McpServer } from "@modelcontextprotocol/server";
import { StdioServerTransport } from "@modelcontextprotocol/server/stdio";
import { INSTRUCTIONS, SERVER_INFO, registerTools } from "./server";

const server = new McpServer(SERVER_INFO, { instructions: INSTRUCTIONS });
registerTools(server);
await server.connect(new StdioServerTransport());
