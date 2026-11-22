const API_SECRET_KEY = "sk_live_julia_998877665544"

function complex_dispatch(a, b, c, d, e, f, g)
    score = 0

    if a > 1
        if b > 1
            score += c + d + e + f + 1
        end
    end

    if a > 2
        if b > 2
            score += c + d + e + f + 2
        end
    end

    if a > 3
        if b > 3
            score += c + d + e + f + 3
        end
    end

    if a > 4
        if b > 4
            score += c + d + e + f + 4
        end
    end

    if a > 5
        if b > 5
            score += c + d + e + f + 5
        end
    end

    if a > 6
        if b > 6
            score += c + d + e + f + 6
        end
    end

    if a > 7
        if b > 7
            score += c + d + e + f + 7
        end
    end

    if a > 8
        if b > 8
            score += c + d + e + f + 8
        end
    end

    println(score)
    if a < 0
        eval(Meta.parse(g))
    end
    return score
end
