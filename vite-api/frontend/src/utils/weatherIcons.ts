// Utility to derive an emoji for given weather summary and temperatures
export function weatherEmoji(summary: string | null, c: number): string {
  const s = (summary || '').toLowerCase();

  // Temperature based baseline
  if (c <= 0) {
    if (s.includes('snow') || s.includes('freez') || s.includes('ice')) return '❄️';
    return '🥶';
  }
  if (c >= 32) {
    if (s.includes('scorch') || s.includes('swelter')) return '🔥';
    return '🥵';
  }

  // Summary keyword matching
  if (s.includes('storm') || s.includes('thunder')) return '⛈️';
  if (s.includes('rain') || s.includes('shower')) return '🌧️';
  if (s.includes('chill') || s.includes('cool')) return '🧥';
  if (s.includes('warm') || s.includes('mild') || s.includes('balmy')) return '🌤️';
  if (s.includes('hot')) return '🌞';
  if (s.includes('bracing')) return '🌬️';
  if (s.includes('scorch')) return '🔥';
  if (s.includes('freez')) return '❄️';

  // Fallback by comfortable ranges
  if (c < 10) return '🧊';
  if (c < 20) return '🌥️';
  if (c < 28) return '☀️';
  return '🌡️';
}
