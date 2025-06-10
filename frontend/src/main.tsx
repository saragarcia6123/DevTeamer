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
import Login from './pages/login/Login.tsx'
import Scaffold from './Scaffold.tsx'
import LoginSuccess from './pages/login/LoginSuccess.tsx'
import Register from './pages/register/Register.tsx'
import RegisterSuccess from './pages/register/RegisterSuccess.tsx'
import ConfirmLogin from './pages/login/ConfirmLogin.tsx'
import VerifySuccess from './pages/verify/VerifySuccess.tsx'

export const optionalEmail = z.preprocess(
  (val) => {
    return typeof val === 'string' && z.string().email().safeParse(val).success
      ? val
      : undefined;
  },
  z.string().email().optional()
);

const rootRoute = createRootRoute({
  component: Root
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: Home,
});

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'login',
  component: Login,
});

const loginSuccessRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'login-success',
  validateSearch: z.object({email: optionalEmail}),
  component: LoginSuccess,
});

const registerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'register',
  validateSearch: z.object({email: optionalEmail}),
  component: Register,
});

const registerSuccessRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'register-success',
  validateSearch: z.object({email: optionalEmail}),
  component: RegisterSuccess,
});

const confirmLoginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'confirm-login',
  validateSearch: z.object({email: optionalEmail}),
  component: ConfirmLogin,
});

const profileRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'profile',
  component: Profile,
});

const verifySuccessRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: 'verify-success',
  component: VerifySuccess,
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  loginRoute,
  confirmLoginRoute,
  loginSuccessRoute,
  registerRoute,
  registerSuccessRoute,
  verifySuccessRoute,
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
