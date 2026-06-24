// Generate placeholder symbol sprites (PNG) for Prism Path.
// Run: node apps/prism-path/tools/gen_placeholders.mjs
// These are CONFIG-SLOT placeholders — final art drops in by replacing these files.
import sharp from 'sharp';
import { mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const OUT = join(here, '..', 'static', 'assets', 'symbols');
mkdirSync(OUT, { recursive: true });

const SIZE = 192;

const SYMS = [
	{ id: 'L1', sub: '10', c1: '#9AD8FF', c2: '#2E86C1' },
	{ id: 'L2', sub: 'J', c1: '#8FE9CE', c2: '#1FA37A' },
	{ id: 'L3', sub: 'Q', c1: '#AAB4F5', c2: '#4A57C7' },
	{ id: 'L4', sub: 'K', c1: '#D2ADF3', c2: '#7A3FB0' },
	{ id: 'L5', sub: 'A', c1: '#9AC4F5', c2: '#2E6FC1' },
	{ id: 'H1', sub: 'FIRE', c1: '#FFB48F', c2: '#E0381A' },
	{ id: 'H2', sub: 'WATER', c1: '#9AD8FF', c2: '#1A74E0' },
	{ id: 'H3', sub: 'NATURE', c1: '#A8EC9A', c2: '#2EA01A' },
	{ id: 'H4', sub: 'ARCANE', c1: '#D2ADFF', c2: '#7A1AE0' },
];

function tile({ id, sub, c1, c2, defs = '', fill }) {
	const bg = fill || `url(#g)`;
	const grad = fill
		? defs
		: `<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
				<stop offset="0" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/>
			</linearGradient>${defs}</defs>`;
	return Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${SIZE}" height="${SIZE}" viewBox="0 0 ${SIZE} ${SIZE}">
		${grad}
		<rect x="10" y="10" width="${SIZE - 20}" height="${SIZE - 20}" rx="26" fill="${bg}" stroke="rgba(255,255,255,0.85)" stroke-width="5"/>
		<rect x="10" y="10" width="${SIZE - 20}" height="${SIZE - 20}" rx="26" fill="none" stroke="rgba(0,0,0,0.35)" stroke-width="2"/>
		<text x="50%" y="46%" text-anchor="middle" font-family="Arial, sans-serif" font-size="64" font-weight="800"
			fill="#ffffff" stroke="rgba(0,0,0,0.45)" stroke-width="2" paint-order="stroke">${id}</text>
		<text x="50%" y="70%" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" font-weight="700"
			fill="rgba(255,255,255,0.95)">${sub}</text>
	</svg>`);
}

const jobs = SYMS.map((s) => ({ id: s.id, svg: tile(s) }));

// WILD — prismatic rainbow
jobs.push({
	id: 'WILD',
	svg: tile({
		id: 'WILD',
		sub: 'PRISM BEAST',
		fill: 'url(#prism)',
		defs: `<linearGradient id="prism" x1="0" y1="0" x2="1" y2="1">
			<stop offset="0" stop-color="#ff4d6d"/><stop offset="0.25" stop-color="#ffd24a"/>
			<stop offset="0.5" stop-color="#5bd06b"/><stop offset="0.75" stop-color="#38b6ff"/>
			<stop offset="1" stop-color="#b06bff"/></linearGradient>`,
	}),
});

// SCAT — gold scatter
jobs.push({
	id: 'SCAT',
	svg: tile({
		id: 'SCAT',
		sub: 'SCATTER',
		fill: 'url(#gold)',
		defs: `<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">
			<stop offset="0" stop-color="#ffe79a"/><stop offset="1" stop-color="#d9a521"/></linearGradient>`,
	}),
});

// prismBeast — the firing-beast overlay sprite used by PrismFx
jobs.push({
	id: 'prismBeast',
	svg: tile({
		id: 'BEAST',
		sub: 'PRISM',
		fill: 'url(#beast)',
		defs: `<radialGradient id="beast" cx="0.5" cy="0.42" r="0.72">
			<stop offset="0" stop-color="#c79bff"/><stop offset="0.55" stop-color="#7a1ae0"/>
			<stop offset="1" stop-color="#1b0140"/></radialGradient>`,
	}),
});

const results = await Promise.all(
	jobs.map((j) => sharp(j.svg).png().toFile(join(OUT, `${j.id}.png`)).then(() => j.id)),
);
console.log('generated placeholder sprites:', results.join(', '));
console.log('out dir:', OUT);
