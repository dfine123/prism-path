import type { Graphics } from 'pixi.js';

// ---------------------------------------------------------------------------------------
// SUPER STUDIOS GLYPH SET — the console's icon language, drawn as vectors so it is crisp at
// any DPI and needs no atlas. Kept as a PURE function (not a component) so the exact shipped
// geometry can be rendered offscreen and inspected.
//
// House rules, applied to every glyph:
//   1. EVERY arc is preceded by an explicit moveTo. Pixi continues the current path into an
//      arc's start point otherwise, which drew a spur from the origin across the icon — the
//      "deformed" spin and sound glyphs were exactly this.
//   2. One optical weight: strokes derive from STROKE_RATIO, so a plus and a gear read with
//      the same ink density at the same size.
//   3. Glyphs are drawn inside a unit box of `size` centred on (0,0) and stay within ~0.86
//      of it, so different icons look the same size on the same key.
//   4. Shapes are built from real construction (tangent arrowheads, true gear teeth,
//      a speaker with an actual cone) instead of approximations that fall apart when scaled.
// ---------------------------------------------------------------------------------------

export type GlyphName =
	| 'decrease'
	| 'increase'
	| 'menu'
	| 'menuExit'
	| 'turbo'
	| 'autoSpin'
	| 'spin'
	| 'stop'
	| 'star'
	| 'payTable'
	| 'info'
	| 'settings'
	| 'soundOn'
	| 'soundOff'
	| 'chevronDown';

const STROKE_RATIO = 0.115;

/** Arrowhead whose axis is TANGENT to a circle at `ang` — the head sits on the arc's end
 *  and points the way the arc travels, instead of floating beside it. */
const tangentArrowHead = (
	g: Graphics,
	ang: number,
	radius: number,
	len: number,
	halfWidth: number,
	dir: 1 | -1,
	color: number,
) => {
	const cx = Math.cos(ang) * radius;
	const cy = Math.sin(ang) * radius;
	// unit tangent (direction of travel) and unit radial (outward)
	const tx = -Math.sin(ang) * dir;
	const ty = Math.cos(ang) * dir;
	const rx = Math.cos(ang);
	const ry = Math.sin(ang);
	g.poly([
		cx + tx * len, cy + ty * len, // tip, along the arc
		cx + rx * halfWidth, cy + ry * halfWidth, // outer corner
		cx - rx * halfWidth, cy - ry * halfWidth, // inner corner
	]).fill({ color });
};

export const drawGlyph = (
	g: Graphics,
	{ icon, size, color }: { icon: GlyphName; size: number; color: number },
) => {
	const s = size;
	const lw = Math.max(2, s * STROKE_RATIO);
	const stroke = { width: lw, color, cap: 'round' as const, join: 'round' as const };

	switch (icon) {
		case 'decrease': {
			const a = s * 0.27;
			g.moveTo(-a, 0).lineTo(a, 0).stroke(stroke);
			break;
		}
		case 'increase': {
			// a plus reads optically LARGER than a circular glyph of equal extent, so its arms
			// stop shorter than the nominal box
			const a = s * 0.27;
			g.moveTo(-a, 0).lineTo(a, 0).stroke(stroke);
			g.moveTo(0, -a).lineTo(0, a).stroke(stroke);
			break;
		}
		case 'menu': {
			const a = s * 0.32;
			for (const dy of [-0.26, 0, 0.26]) {
				g.moveTo(-a, s * dy).lineTo(a, s * dy).stroke(stroke);
			}
			break;
		}
		case 'menuExit': {
			const a = s * 0.28;
			g.moveTo(-a, -a).lineTo(a, a).stroke(stroke);
			g.moveTo(-a, a).lineTo(a, -a).stroke(stroke);
			break;
		}
		case 'chevronDown': {
			// single chevron (drawer fold toggle) — rotates 180 for the unfold state
			const w = s * 0.3;
			const h = s * 0.16;
			g.moveTo(-w, -h).lineTo(0, h).lineTo(w, -h).stroke(stroke);
			break;
		}
		case 'turbo': {
			// fast-forward: two chevrons, nested so they read as one motion mark
			const h = s * 0.28;
			const w = s * 0.2;
			for (const dx of [-s * 0.2, s * 0.08]) {
				g.moveTo(dx, -h)
					.lineTo(dx + w, 0)
					.lineTo(dx, h)
					.stroke(stroke);
			}
			break;
		}
		case 'spin':
		case 'autoSpin': {
			// Circular arrow. The arc leaves a gap for the head, and the head is built on the
			// tangent at the arc's leading end so the whole mark reads as one continuous sweep.
			const r = s * 0.31;
			const headLen = s * 0.2;
			const headHalf = s * 0.145;
			// autoSpin runs the other way and leaves a wider mouth (the spin counter sits
			// inside it), so the two never read as the same button
			const dir: 1 | -1 = icon === 'spin' ? 1 : -1;
			const start = icon === 'spin' ? -Math.PI * 0.62 : -Math.PI * 0.38;
			const sweep = icon === 'spin' ? Math.PI * 1.62 : Math.PI * 1.5;
			const a0 = start;
			const a1 = start + sweep * dir;
			g.moveTo(Math.cos(a0) * r, Math.sin(a0) * r);
			g.arc(0, 0, r, a0, a1, dir === -1).stroke(stroke);
			tangentArrowHead(g, a1, r, headLen, headHalf, dir, color);
			break;
		}
		case 'stop': {
			// a solid square reads optically SMALLER than an outlined glyph of equal extent
			const a = s * 0.28;
			g.roundRect(-a, -a, a * 2, a * 2, a * 0.32).fill({ color });
			break;
		}
		case 'star': {
			// 5-point star with a slightly fattened inner radius — a thin-waisted star reads
			// as spiky at small sizes. No painted-on "glint": the key's own specular does it.
			const R = s * 0.44;
			const rIn = R * 0.47;
			const pts: number[] = [];
			for (let i = 0; i < 10; i++) {
				const a = -Math.PI / 2 + (i * Math.PI) / 5;
				const rad = i % 2 === 0 ? R : rIn;
				pts.push(Math.cos(a) * rad, Math.sin(a) * rad);
			}
			g.poly(pts).fill({ color });
			// rounded silhouette: a same-colour stroke softens the points without changing shape
			g.poly(pts).stroke({ width: Math.max(1.5, s * 0.06), color, join: 'round' });
			break;
		}
		case 'payTable': {
			// A TABLE: framed rows. Rendered side by side at the real console size (~34px), a
			// coin stack — two coins or three — collapses into an illegible smudge, while the
			// framed rows stay crisp and unmistakably mean "pay table".
			const w = s * 0.72;
			const h = s * 0.78;
			const frame = Math.max(2, s * 0.095);
			g.roundRect(-w / 2, -h / 2, w, h, s * 0.12).stroke({
				width: frame,
				color,
				join: 'round',
			});
			const inset = s * 0.13;
			for (const dy of [-0.19, 0, 0.19]) {
				g.moveTo(-w / 2 + inset, s * dy)
					.lineTo(w / 2 - inset, s * dy)
					.stroke({ width: Math.max(2, s * 0.082), color, cap: 'round' });
			}
			break;
		}
		case 'info': {
			const r = s * 0.36;
			g.circle(0, 0, r).stroke({ ...stroke, width: Math.max(2, s * 0.1) });
			g.circle(0, -s * 0.16, Math.max(1.6, s * 0.055)).fill({ color });
			g.moveTo(0, -s * 0.02).lineTo(0, s * 0.19).stroke({ ...stroke, width: Math.max(2, s * 0.1) });
			break;
		}
		case 'settings': {
			// real gear: one closed outline alternating tooth/valley radii, plus a hub hole.
			// (Radial spokes off a ring read as a sun, which is what the old glyph did.)
			const teeth = 8;
			const rOut = s * 0.4;
			const rIn = s * 0.29;
			const pts: number[] = [];
			const step = (Math.PI * 2) / teeth;
			const toothHalf = step * 0.28; // angular half-width of the tooth crown
			const valleyHalf = step * 0.2;
			for (let i = 0; i < teeth; i++) {
				const c = i * step - Math.PI / 2;
				pts.push(Math.cos(c - toothHalf) * rOut, Math.sin(c - toothHalf) * rOut);
				pts.push(Math.cos(c + toothHalf) * rOut, Math.sin(c + toothHalf) * rOut);
				const v = c + step / 2;
				pts.push(Math.cos(v - valleyHalf) * rIn, Math.sin(v - valleyHalf) * rIn);
				pts.push(Math.cos(v + valleyHalf) * rIn, Math.sin(v + valleyHalf) * rIn);
			}
			g.poly(pts).fill({ color });
			// hub: punched out by drawing the key colour is not possible here (no knockout),
			// so the hole is cut with a ring stroke in the surface tone via `cut`
			g.circle(0, 0, s * 0.135).cut();
			break;
		}
		case 'soundOn':
		case 'soundOff': {
			// speaker: box + cone as ONE polygon (a seam between two shapes shows at size)
			const bx0 = -s * 0.4;
			const bx1 = -s * 0.16;
			const by = s * 0.13;
			const cx = -s * 0.02;
			const cy = s * 0.32;
			g.poly([
				bx0, -by,
				bx1, -by,
				cx, -cy,
				cx, cy,
				bx1, by,
				bx0, by,
			]).fill({ color });
			if (icon === 'soundOn') {
				// two waves, each an arc with an explicit moveTo (no spur back to the cone)
				const waveStroke = { ...stroke, width: Math.max(2, s * 0.095) };
				for (const [rad, span] of [
					[s * 0.17, 0.34],
					[s * 0.31, 0.3],
				] as const) {
					const a0 = -Math.PI * span;
					const a1 = Math.PI * span;
					g.moveTo(cx + Math.cos(a0) * rad, Math.sin(a0) * rad);
					g.arc(cx, 0, rad, a0, a1).stroke(waveStroke);
				}
			} else {
				// muted: a clean X clear of the cone
				const x0 = s * 0.13;
				const x1 = s * 0.38;
				const yy = (x1 - x0) / 2;
				g.moveTo(x0, -yy).lineTo(x1, yy).stroke(stroke);
				g.moveTo(x0, yy).lineTo(x1, -yy).stroke(stroke);
			}
			break;
		}
	}
};
