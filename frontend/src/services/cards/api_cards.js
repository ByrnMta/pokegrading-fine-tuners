import { postFormData } from '../api_client'

export async function postCard(formData) {
    return postFormData('/catalogo/carta', formData)
}
