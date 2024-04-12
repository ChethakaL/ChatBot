module.exports = {
  apps: [{
    name: 'infigo-chatbot',
    script: 'app.py',
    interpreter: './venv/bin/python',
    args: 'run',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      FLASK_APP: 'app.py',
      FLASK_ENV: 'production',
      PORT: 5000,
    },
  }],
};
