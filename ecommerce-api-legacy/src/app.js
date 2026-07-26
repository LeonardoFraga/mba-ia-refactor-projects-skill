// Composition root: wire config, DB, routers and error handling, then listen.
'use strict';

const express = require('express');
const settings = require('./config/settings');
const db = require('./config/database');

const checkoutRoutes = require('./routes/checkoutRoutes');
const adminRoutes = require('./routes/adminRoutes');
const userRoutes = require('./routes/userRoutes');
const { errorHandler, notFound } = require('./middlewares/errorHandler');

async function bootstrap() {
    await db.init();

    const app = express();
    app.use(express.json());

    // Routers (each declares its own full path).
    app.use(checkoutRoutes);
    app.use(adminRoutes);
    app.use(userRoutes);

    // Cross-cutting concerns last.
    app.use(notFound);
    app.use(errorHandler);

    app.listen(settings.port, () => {
        console.log(`Frankenstein LMS rodando na porta ${settings.port}...`);
    });
}

bootstrap().catch((err) => {
    console.error('Falha ao iniciar a aplicação:', err.message);
    process.exit(1);
});
