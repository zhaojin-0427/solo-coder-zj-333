export function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
}

export function camelToSnake(str: string): string {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
}

export function convertKeysSnakeToCamel<T = any>(obj: any): T {
  if (obj === null || obj === undefined) {
    return obj as T
  }

  if (Array.isArray(obj)) {
    return obj.map(item => convertKeysSnakeToCamel(item)) as unknown as T
  }

  if (typeof obj !== 'object') {
    return obj as T
  }

  const result: Record<string, any> = {}

  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const camelKey = snakeToCamel(key)
      const value = obj[key]

      if (typeof value === 'object' && value !== null) {
        result[camelKey] = convertKeysSnakeToCamel(value)
      } else {
        result[camelKey] = value
      }
    }
  }

  return result as T
}

export function convertKeysCamelToSnake(obj: any): any {
  if (obj === null || obj === undefined) {
    return obj
  }

  if (Array.isArray(obj)) {
    return obj.map(item => convertKeysCamelToSnake(item))
  }

  if (typeof obj !== 'object') {
    return obj
  }

  const result: Record<string, any> = {}

  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const snakeKey = camelToSnake(key)
      const value = obj[key]

      if (typeof value === 'object' && value !== null) {
        result[snakeKey] = convertKeysCamelToSnake(value)
      } else {
        result[snakeKey] = value
      }
    }
  }

  return result
}
