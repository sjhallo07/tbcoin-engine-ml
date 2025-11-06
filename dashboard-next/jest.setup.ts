import '@testing-library/jest-dom'
import 'whatwg-fetch'

import { TextDecoder, TextEncoder } from 'util'

if (!global.TextEncoder) {
	;(global as unknown as { TextEncoder: typeof TextEncoder }).TextEncoder = TextEncoder
}

if (!global.TextDecoder) {
	;(global as unknown as { TextDecoder: typeof TextDecoder }).TextDecoder = TextDecoder as typeof global.TextDecoder
}
