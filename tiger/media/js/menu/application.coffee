this.App =
    sections: new Sections
    views: {}
    init: ->
        _.each sectionIds, (sectionId) -> 
            $.get "/menu/section/" + sectionId + ".json", (data) ->
                section = new Section(JSON.parse data)
                App.sections.add section
                if !App.controller
                    @controller = new MenuController
                    Backbone.history.start()

App.init()
