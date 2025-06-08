import { describe, expect, test } from 'vitest'
import { render, screen } from '@testing-library/react'
import Home from './pages/Home.tsx'

describe('App', () => {
  test('renders', () => {
    render(<Home />)
    expect(screen.getByText('Learn React')).toBeDefined()
  })
})
