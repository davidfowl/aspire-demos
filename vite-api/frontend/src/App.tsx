import './App.css'
import { WeatherDisplay } from './components/WeatherDisplay'

function App() {
  return (
    <div className="layout-center">
      <div className="App">
        <header className="App-header">
          <h1>Weather App</h1>
          <p>A Vite React app calling .NET Aspire Weather API</p>
        </header>
        <main>
          <WeatherDisplay />
        </main>
      </div>
    </div>
  )
}

export default App
