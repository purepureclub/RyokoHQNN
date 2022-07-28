import { render, screen } from '@testing-library/react';
import App from './App';

test('renders canvas', () => {
  render(<App />);
  const canvasElement = screen.getByText(/量子コンピューターで画像識別/i);
  expect(canvasElement).toBeInTheDocument();
});
