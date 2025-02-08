// Types

// Color map related
export type ColorMapLimit = number | null
export type ColorMapColor = string
export type ColorMapLabel = string
export type ColorMapDefItem = [ColorMapLimit, ColorMapColor, ColorMapLabel]
export type ColorMapDef = ColorMapDefItem[]
export interface ColorMapItem {
    limit: ColorMapLimit
    color: ColorMapColor
    label: ColorMapLabel
}
export interface ColorMap {
    name: string
    items: ColorMapItem[]
}
