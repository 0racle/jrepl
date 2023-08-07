Repr =: {{
    if. 0 = (4!:0) y do.
        (quote"1^:(((2 ^ 1 17 18) e.~ 3!:0))) L: 0 ". > y
    else.
        f =. < (5!:5) y
        if. (1 2 3) e.~ (4!:0) f do.
            Repr f
        else.
            if. '^\d : ' {.@rxE > f do.
                > f
            else.
                ((5!:5)) y
            end.
        end.
    end.
}}

