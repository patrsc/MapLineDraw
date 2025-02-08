// Types
import { CircleMarker, Polyline } from "leaflet"

// Common
export type int = number
export type float = number

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
export interface PreparedColorMap {
    colors: ColorMapColor[]
    limits: number[]
    factors: number[]
}

// Coordinates
export interface CartesianPoint {
    x: number
    y: number
}
export interface GlobePoint {
    lat: number
    lon: number
}

// Project
export interface ProjectInfo {
    name: string
    description: string
    author: string
}
export interface Curve {
    name: string
    controlPoints: GlobePoint[]
    closed: boolean
}
export type MapBackground = string
export interface MapSettings {
    center: GlobePoint
    zoom: number
    background: MapBackground,
}
export interface Settings {
    selectedColorMapIndex: number
    map: MapSettings
}

export interface Project {
    info: ProjectInfo
    curves: Curve[]
    colorMaps: ColorMap[]
    settings: Settings
}


// Cache
export interface SplineData {
    degree: int
    lat: float[]
    lon: float[]
    distance: float[]
    curvature: float[]
    speed: float[]
}
export interface Spline {
    requestedId: number
    id: number
    data: null | SplineData
}
export type LayerItem = CircleMarker | Polyline
export interface CurveCacheItem {
    points: CircleMarker[]
    spline: Spline
    layers: LayerItem[]
}

export type CurveCache = CurveCacheItem[]
