this.App =
    sections: new Sections
    views: {}
    init: ->
        # check for menu_key cookie
        sections = JSON.parse(localStorage.getItem "menu")
        for section in sections
            do (section) ->
                App.sections.add(new Section section)
        @cart = new Cart line_items
        if not App.controller?
            App.controller = new MenuController
            Backbone.history.start()
        ($ "#menu-main").attr "href", "/menu/#"

    # Returns a unicode spinny character generator function!
    spinner: ->
        index = 0
        states = [
            "\u2596"
            "\u2598"
            "\u259D"
            "\u2597"
        ]
        spin = ->
            index = (index + 1) % states.length
            states[index]

App.init()
new CartSummaryView()
