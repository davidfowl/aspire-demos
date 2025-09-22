import type { WeatherForecast } from '../types/weather';

export class WeatherService {
  static async getWeatherForecast(): Promise<WeatherForecast[]> {
    try {
      const response = await fetch(`/weatherforecast`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching weather forecast:', error);
      throw error;
    }
  }
}