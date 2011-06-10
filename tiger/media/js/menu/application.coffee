this.App =
    sections: new Sections
    views: {}
    init: ->
        # check for menu_key cookie
        sections = JSON.parse(localStorage.getItem "menu")
        for section in sections
            do (section) ->
                App.sections.add(new Section section)
                if not App.controller?
                    App.controller = new MenuController
                    Backbone.history.start()

App.init()
