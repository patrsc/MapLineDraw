const highspeedTrain = [
    [null, '#9C59FF', '400+'],
    [400, '#009B33', '350+'],
    [350, '#00D219', '300+'],
    [300, '#A1FC00', '250+'],
    [250, '#FFFF00', '200+'],
    [200, '#FF9500', '160+'],
    [160, '#FF0000', '<160'],
]

const lowspeedTrain = [
    [null, '#9C59FF', '200+'],
    [200, '#009B33', '160+'],
    [160, '#00D219', '120+'],
    [120, '#A1FC00', '100+'],
    [100, '#FFFF00', '80+'],
    [80, '#FF9500', '60+'],
    [60, '#FF0000', '<60'],
]

function toObject(item) {
    return {limit: item[0], color: item[1], label: item[2]}
}

export const colorMaps = [
    {
        name: "High-speed train",
        items: highspeedTrain.map(toObject),
    },
    {
        name: "Low-speed train",
        items: lowspeedTrain.map(toObject),
    }
]

export function getColor(speed, items) {
    const f = 1.15
    for (let i = items.length - 1; i >= 0; i--) {
        const limit = items[i].limit
        const color = items[i].color
        if (speed < limit || limit === null) {
            return [ color, Math.pow(f, i) ]
        }
    }
}
