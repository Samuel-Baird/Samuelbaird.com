// Canonical MCP endpoint: https://samuelbaird.com/latter-day-stats/mcp.
// Same handler as /api/mcp, which stays as an alias for existing connectors
// (as do the legacy host's /api/mcp and /mcp).
export { GET, POST } from "../api/mcp/route";
