// Import final symbol art (SVGs wrapping embedded rasters) -> square transparent PNGs that drop
// straight into the config-slot manifest (file swap, no code change for the base symbols).
// Large royals (~17MB) exceed librsvg's XML buffer, so we fall back to decoding the largest
// embedded raster directly. Run: node apps/prism-path/tools/import_art.mjs
import sharp from 'sharp';
import { readFileSync, mkdirSync } from 'node:fs';

const HOME = 'C:/Users/Streaming';
const OUT = 'C:/Users/Streaming/prism-path/frontend/apps/prism-path/static/assets/symbols';
mkdirSync(OUT, { recursive: true });
const SIZE = 256;

// source SVG -> output symbol id(s)
const JOBS = [
	['Downloads/Red_Symbol.svg', ['H1']], // Fire
	['Downloads/blue_symbol.svg', ['H2']], // Water
	['Downloads/green_symbol (1).svg', ['H3']], // Nature
	['Downloads/purple_symbol.svg', ['H4']], // Arcane
	['Downloads/J_symbol_prism.svg', ['L2']], // J
	['Downloads/Q_Symbol_prism.svg', ['L3']], // Q
	['Downloads/K_symbol_prism-e72a-4bf8-ace4-0619af1c7254.svg', ['L4']], // K
	['Downloads/A_Symbol_Prism.svg', ['L5']], // A
	['Downloads/Beast Up.svg', ['beastUp']],
	['Downloads/Beast Down.svg', ['beastDown', 'WILD']], // WILD = idle/board beast
	['Downloads/Beast_Left.svg', ['beastLeft']],
	['Downloads/Beast Right.svg', ['beastRight']],
];

function largestEmbeddedRaster(svgText) {
	const re = /data:image\/(?:png|jpe?g);base64,([A-Za-z0-9+/=]+)/g;
	let m;
	let best = null;
	let bestLen = 0;
	while ((m = re.exec(svgText))) {
		if (m[1].length > bestLen) {
			bestLen = m[1].length;
			best = m[1];
		}
	}
	return best ? Buffer.from(best, 'base64') : null;
}

async function rasterize(src) {
	try {
		return await sharp(src, { density: 200 })
			.resize(SIZE, SIZE, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
			.png()
			.toBuffer();
	} catch (e) {
		// librsvg buffer limit on huge SVGs -> decode the largest embedded raster instead
		const buf = largestEmbeddedRaster(readFileSync(src, 'utf8'));
		if (!buf) throw e;
		const out = await sharp(buf)
			.resize(SIZE, SIZE, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
			.png()
			.toBuffer();
		return out;
	}
}

for (const [rel, ids] of JOBS) {
	try {
		const png = await rasterize(`${HOME}/${rel}`);
		for (const id of ids) {
			const dst = `${OUT}/${id}.png`;
			await sharp(png).toFile(dst);
		}
		console.log('ok', ids.join('+'), '<-', rel);
	} catch (e) {
		console.log('ERR', ids.join('+'), rel, e.message.split('\n')[0]);
	}
}
console.log('done. (L1=10 and SCAT remain placeholders — no art supplied)');
