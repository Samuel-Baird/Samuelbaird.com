/** Remote MCP endpoint (Streamable HTTP): https://<deployment>/mcp */
import { createMcpHandler } from "mcp-handler";
import { INSTRUCTIONS, SERVER_INFO, registerTools } from "../../src/server";

export const maxDuration = 60;

const handler = createMcpHandler(registerTools, {
  serverInfo: SERVER_INFO,
  instructions: INSTRUCTIONS,
});

export { handler as GET, handler as POST, handler as DELETE };
