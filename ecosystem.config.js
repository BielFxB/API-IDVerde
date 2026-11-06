module.exports = {
  apps: [
    {
      name: "idverde-api",
      cwd: "./",
      script: "./.venv/bin/gunicorn",
      args: "app:app --bind 127.0.0.1:5000 --workers 1 --threads 4 --timeout 120",
      interpreter: "none",
      autorestart: true,
      watch: false,
      max_memory_restart: "600M",
      env: {
        PORT: 5000,
        FLASK_ENV: "production"
      }
    }
  ]
};
