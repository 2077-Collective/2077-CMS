import { atom } from 'nanostores'

export const loading = atom<boolean>(false)

export function setLoading(value: boolean) {
    loading.set(value)
}
