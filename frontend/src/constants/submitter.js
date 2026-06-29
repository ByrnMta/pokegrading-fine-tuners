export const SUBMITTER_INITIAL_METADATA = {
    nombre: '',
    set_name: '',
    numero: '',
    edicion: '',
    idioma: '',
    acabado: '',
    rareza: '',
    tipo: '',
    hp: '',
    ilustrador: '',
    anio_impresion: '',
}

export const SUBMITTER_IMAGE_SIDE = {
    FRONT: 'front',
    BACK: 'back',
}

export const SUBMITTER_IMAGE_LABEL = {
    FRONT: 'Imagen frontal (JPEG, PNG, HEIC) *',
    BACK: 'Imagen del reverso (JPEG, PNG, HEIC) *',
}

export const SUBMITTER_USE_MOCK = false

/**
 * Opciones de set + acabado disponibles para la selección en el formulario.
 * Cada entrada se muestra como "Set · Acabado" en la UI pero se envía
 * al backend como dos campos separados: set_name y acabado.
 */
export const CARD_SET_OPTIONS = [
    { set_name: 'Base Set',        acabado: 'Holo' },
    { set_name: 'Base Set',        acabado: 'Non-Holo' },
    { set_name: 'Jungle',          acabado: 'Holo' },
    { set_name: 'Jungle',          acabado: 'Non-Holo' },
    { set_name: 'Fossil',          acabado: 'Holo' },
    { set_name: 'Fossil',          acabado: 'Non-Holo' },
    { set_name: 'Scarlet & Violet', acabado: 'Reverse Holo' },
    { set_name: 'Scarlet & Violet', acabado: 'Holo' },
    { set_name: 'Scarlet & Violet', acabado: 'Non-Holo' },
    { set_name: 'Paldea Evolved',  acabado: 'Reverse Holo' },
    { set_name: 'Paldea Evolved',  acabado: 'Holo' },
    { set_name: 'Paldea Evolved',  acabado: 'Non-Holo' },
    { set_name: 'Obsidian Flames', acabado: 'Reverse Holo' },
    { set_name: 'Obsidian Flames', acabado: 'Non-Holo' },
    { set_name: 'Celebrations',    acabado: 'Classic' },
    { set_name: 'Hidden Fates',    acabado: 'Shiny' },
]