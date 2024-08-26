import { atom } from 'nanostores'

export const category = atom<string | undefined>()
export const searchTerm = atom<string>('')

export function setCategory(c: string) {
    category.set(c)
}

export function clearCategories() {
    category.set(undefined)
}
