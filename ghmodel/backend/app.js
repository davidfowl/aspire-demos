import express from 'express';
import OpenAI from 'openai';
import { parseConnectionString } from './connectionString.js';

const cs = parseConnectionString('model');
if (!cs.isValid) {
    console.warn('Connection string validation errors:\n' + cs.errors.join('\n'));
}
const { endpoint, key, model } = cs;

// Configure OpenAI client for model inference endpoint.
const client = new OpenAI({
    apiKey: key,
    baseURL: endpoint
});

const app = express();
app.use(express.json());

app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.get('/quote', async (req, res) => {
    try {
        if (!cs.isValid) {
            return res.status(500).json({ error: 'Model endpoint not configured.', details: cs.errors });
        }

        const prompt = 'Provide a short, original, uplifting programming productivity quote (no more than 20 words). Return only the quote.';

        const completion = await client.chat.completions.create({
            model,
            messages: [
                { role: 'system', content: 'You generate concise inspirational quotes.' },
                { role: 'user', content: prompt }
            ]
        });

        const text = completion.choices?.[0]?.message?.content?.trim();
        if (!text) {
            return res.status(502).json({ error: 'No content returned from model.' });
        }
        res.json({ quote: text });
    } catch (err) {
        console.error('Error generating quote', err);
        res.status(500).json({ error: 'Failed to generate quote.' });
    }
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Backend listening on port ${port}`);
});
