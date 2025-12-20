/**
 * useSparkline - Generate SVG sparkline paths for coins
 */
export function useSparkline() {
    /**
     * Generate sparkline SVG path from coin data
     * Uses sparkline_7d data if available, otherwise generates from 24h change
     */
    const generateSparkline = (coin: any, width = 60, height = 24): string => {
        const change = parseFloat(coin.change24h || coin.change_24h) || 0
        let data: number[] = []

        // Use real sparkline data if available
        const sparkline = coin.sparkline_7d?.price || coin.sparkline_7d || coin.sparkline
        if (Array.isArray(sparkline) && sparkline.length > 0) {
            // Downsample to ~24 points for performance
            const step = Math.max(1, Math.floor(sparkline.length / 24))
            for (let i = 0; i < sparkline.length; i += step) {
                data.push(parseFloat(sparkline[i]) || 0)
            }
            // Ensure we have the last point
            if (data[data.length - 1] !== sparkline[sparkline.length - 1]) {
                data.push(parseFloat(sparkline[sparkline.length - 1]) || 0)
            }
        } else {
            // Fallback: Generate pseudo-random but deterministic data
            const seed = (coin.id || coin.coin_id || coin.symbol || 'default')
                .split('')
                .reduce((acc: number, c: string) => acc + c.charCodeAt(0), 0)
            const points = 12

            for (let i = 0; i < points; i++) {
                const noise = (Math.sin(seed * i * 0.5) * 0.5) * Math.abs(change) * 0.3
                const trend = (i / points) * change
                data.push(50 + trend + noise)
            }
        }

        if (data.length < 2) return ''

        const min = Math.min(...data)
        const max = Math.max(...data)
        const range = max - min || 1
        const stepX = width / (data.length - 1)

        // Convert to coordinates with padding
        const coords = data.map((val, i) => ({
            x: i * stepX,
            y: height - ((val - min) / range) * (height - 4) - 2
        }))

        // Build smooth Bezier path using Catmull-Rom spline conversion
        let path = `M${coords[0].x.toFixed(1)},${coords[0].y.toFixed(1)}`

        for (let i = 0; i < coords.length - 1; i++) {
            const p0 = coords[Math.max(0, i - 1)]
            const p1 = coords[i]
            const p2 = coords[i + 1]
            const p3 = coords[Math.min(coords.length - 1, i + 2)]

            const cp1x = p1.x + (p2.x - p0.x) / 6
            const cp1y = p1.y + (p2.y - p0.y) / 6
            const cp2x = p2.x - (p3.x - p1.x) / 6
            const cp2y = p2.y - (p3.y - p1.y) / 6

            path += ` C${cp1x.toFixed(1)},${cp1y.toFixed(1)} ${cp2x.toFixed(1)},${cp2y.toFixed(1)} ${p2.x.toFixed(1)},${p2.y.toFixed(1)}`
        }

        return path
    }

    /**
     * Generate closed path for gradient fill
     */
    const generateSparklineFill = (coin: any, width = 60, height = 24): string => {
        const linePath = generateSparkline(coin, width, height)
        if (!linePath) return ''
        return linePath + ` L${width},${height} L0,${height} Z`
    }

    /**
     * Get stroke color based on change
     */
    const getSparklineColor = (coin: any): string => {
        const change = parseFloat(coin.change24h || coin.change_24h) || 0
        return change >= 0 ? '#00E676' : '#FF5252'
    }

    /**
     * Get gradient ID suffix for unique gradients
     */
    const getGradientId = (coin: any, prefix = 'spark'): string => {
        return `${prefix}-${coin.id || coin.coin_id || coin.symbol}`
    }

    return {
        generateSparkline,
        generateSparklineFill,
        getSparklineColor,
        getGradientId
    }
}
