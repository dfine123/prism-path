// Presentation FX state. winSpeed multiplies the win-presentation clocks (1 = normal).
// A click during the line sequence is the player asking to skip — the winInfo handler
// raises this substantially and every paced surface (line lifecycle, symbol breath,
// wild hold) consumes it via scaled-time accumulation.
export const stateFx = $state({ winSpeed: 1 });
