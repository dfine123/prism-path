// Key a near-white background to transparent + center into a square canvas.
// Usage: node key_white.mjs <src.png> <dst.png> [size]
import sharp from 'sharp';

const [, , src, dst, sizeArg] = process.argv;
const size = Number(sizeArg || 256);

const { data, info } = await sharp(src).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
const { width, height, channels } = info;
for (let i = 0; i < data.length; i += channels) {
	const r = data[i];
	const g = data[i + 1];
	const b = data[i + 2];
	const mn = Math.min(r, g, b);
	if (mn >= 240) data[i + 3] = 0; // near-white background -> fully transparent
	else if (mn >= 216) data[i + 3] = Math.round(((240 - mn) / 24) * 255); // feather the edge
}
await sharp(data, { raw: { width, height, channels } })
	.png()
	.toBuffer()
	.then((buf) =>
		sharp(buf)
			.trim({ threshold: 1 })
			.resize(size, size, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
			.png()
			.toFile(dst),
	);
console.log('keyed ->', dst);
