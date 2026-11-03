const path = require("node:path");

const root = __dirname;
const base = {
  autorestart: true,
  max_restarts: 10,
  min_uptime: "10s",
  time: true,
};

module.exports = {
  apps: [
    {
      ...base,
      name: "ojas-ops-backend",
      cwd: path.join(root, "python"),
      script: path.join(root, "python", ".venv", "bin", "python"),
      args: "apps/sandbox/manage.py runbolt --port 8000",
      interpreter: "none",
      env: {
        PYTHONUNBUFFERED: "1",
      },
    },
    {
      ...base,
      name: "ojas-ops-studio",
      cwd: path.join(root, "typescript", "apps", "ops-studio"),
      script: path.join(root, "typescript", "apps", "ops-studio", "node_modules", ".bin", "next"),
      args: "dev -p 5900",
      interpreter: "bash",
      env: {
        NEXT_PUBLIC_API_URL: "http://localhost:8000",
      },
    },
  ],
};

