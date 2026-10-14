import { createContext, useContext, useEffect, useMemo, useState } from 'react'

import { api, type Profile, type User } from '../lib/api'

/* The provider and its hook intentionally share this module for the auth boundary. */
/* eslint-disable react-refresh/only-export-components */

type AuthContextValue = {
  token: string | null
  user: User | null
  profile: Profile | null
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshProfile: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)
const TOKEN_KEY = 'careerconnect_access_token'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isLoading, setIsLoading] = useState(() => Boolean(localStorage.getItem(TOKEN_KEY)))
  const [error, setError] = useState<string | null>(null)

  const saveSession = async (nextToken: string, nextUser: User) => {
    localStorage.setItem(TOKEN_KEY, nextToken)
    setToken(nextToken)
    setUser(nextUser)
    setProfile(await api.getProfile(nextToken))
  }

  useEffect(() => {
    if (!token) {
      return
    }

    Promise.all([api.currentUser(token), api.getProfile(token)])
      .then(([nextUser, nextProfile]) => {
        setUser(nextUser)
        setProfile(nextProfile)
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY)
        setToken(null)
        setUser(null)
        setProfile(null)
      })
      .finally(() => setIsLoading(false))
  }, [token])

  const value = useMemo<AuthContextValue>(() => ({
    token,
    user,
    profile,
    isLoading,
    error,
    login: async (email, password) => {
      setError(null)
      try {
        const response = await api.login(email, password)
        await saveSession(response.access_token, response.user)
      } catch (caught) {
        const message = caught instanceof Error ? caught.message : 'Unable to log in.'
        setError(message)
        throw caught
      }
    },
    register: async (email, password) => {
      setError(null)
      try {
        const response = await api.register(email, password)
        await saveSession(response.access_token, response.user)
      } catch (caught) {
        const message = caught instanceof Error ? caught.message : 'Unable to create your account.'
        setError(message)
        throw caught
      }
    },
    logout: async () => {
      if (token) await api.logout(token).catch(() => undefined)
      localStorage.removeItem(TOKEN_KEY)
      setToken(null)
      setUser(null)
      setProfile(null)
    },
    refreshProfile: async () => {
      if (token) setProfile(await api.getProfile(token))
    },
  }), [error, isLoading, profile, token, user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within an AuthProvider')
  return context
}
