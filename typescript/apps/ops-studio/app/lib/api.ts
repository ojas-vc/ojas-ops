import { OjasOpsClient } from "@ojas-ops/sdk";

const API_BASE_URL = process.env.NEXT_PUBLIC_OJAS_OPS_API_URL || "http://127.0.0.1:8000";

export const client = new OjasOpsClient({
  baseUrl: API_BASE_URL,
});
