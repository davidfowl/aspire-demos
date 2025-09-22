import { useState, useEffect } from 'react';
import type { WeatherForecast } from '../types/weather';
import { WeatherService } from '../services/weatherService';
import { weatherEmoji } from '../utils/weatherIcons';
import './WeatherDisplay.css';

export function WeatherDisplay() {
  const [weatherData, setWeatherData] = useState<WeatherForecast[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    loadWeatherData();
  }, []);

  const loadWeatherData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await WeatherService.getWeatherForecast();
      setWeatherData(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const refreshData = () => {
    loadWeatherData();
  };

  if (loading) {
    return <div className="loading">Loading weather data...</div>;
  }

  if (error) {
    return (
      <div className="error">
        <p>Error: {error}</p>
        <button onClick={refreshData}>Retry</button>
      </div>
    );
  }

  return (
    <div className="weather-display">
      <div className="weather-header">
        <div className="title-block">
          <h2>5‑Day Outlook</h2>
          {lastUpdated && (
            <div className="last-updated">Updated {lastUpdated.toLocaleTimeString()}</div>
          )}
        </div>
        <div className="actions">
          <button onClick={refreshData} className="refresh-button" aria-label="Refresh forecast">
            ↻ Refresh
          </button>
        </div>
      </div>
      <div className="legend">
        <span>Feels</span><span>Emoji indicates general conditions (temp + summary)</span>
      </div>
      <div className="weather-grid">
        {weatherData.map((f, idx) => {
          const emoji = weatherEmoji(f.summary, f.temperatureC);
          const date = new Date(f.date);
          const dayName = date.toLocaleDateString(undefined, { weekday: 'short' });
          const dayNum = date.getDate();
          return (
            <div key={idx} className="weather-card" aria-label={`Forecast for ${date.toDateString()}`}>
              <div className="card-top">
                <div className="day">{dayName} <span className="day-num">{dayNum}</span></div>
                <div className="emoji" role="img" aria-label={f.summary || 'weather'}>{emoji}</div>
              </div>
              <div className="temps">
                <div className="temp primary">{f.temperatureC}°C</div>
                <div className="temp secondary">{f.temperatureF}°F</div>
              </div>
              <div className="summary-line" title={f.summary || 'No summary'}>
                {f.summary || '—'}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}