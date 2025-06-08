import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import {
  RouterProvider,
  createRootRoute,
  createRoute,
  createRouter,
} from '@tanstack/react-router'
import './styles.css'
import { z } from 'zod'
import reportWebVitals from './reportWebVitals.ts'

import Root from './Root.tsx'
import Home from './pages/Home.tsx'
import Profile from './pages/Profile.tsx'
import Login from './pages/Login.tsx'
import Scaffold from './Scaffold.tsx'
import Verify from './pages/Verify.tsx'
import Register from './pages/Register.tsx'

const rootRoute = createRootRoute({
  component: Root
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: () => {
    return (
      <Scaffold>
        <Home />
      </Scaffold>
    );
  },
})

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'login',
  component: () => {
    return (
      <Scaffold>
        <Login />
      </Scaffold>
    );
  },
})
const registerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'register',
  validateSearch: z.object({
    email: z.preprocess((val) => {
      if (typeof val === 'string') {
        try {
          z.string().email().parse(val);
          return val;
        } catch {
          return undefined;
        }
      }
      return undefined;
    }, z.string().email().optional()),
  }),
  component: () => (
    <Scaffold>
      <Register />
    </Scaffold>
  ),
});


const profileRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'profile',
  component: () => {
    return (
      <Scaffold>
        <Profile />
      </Scaffold>
    );
  },
})

const verifyRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'verify',
  component: () => {
    return (
      <Scaffold>
        <Verify />
      </Scaffold>
    );
  },
})

const routeTree = rootRoute.addChildren([
  indexRoute,
  loginRoute,
  registerRoute,
  verifyRoute,
  profileRoute,
])

const router = createRouter({
  routeTree,
  context: {},
  defaultPreload: 'intent',
  scrollRestoration: true,
  defaultStructuralSharing: true,
  defaultPreloadStaleTime: 0,
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

const rootElement = document.getElementById('app')
if (rootElement && !rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement)

  root.render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>,
  )
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals()
