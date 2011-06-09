class this.ItemView extends Backbone.View
    tagName: "li"

    render: =>
        template = _.template $("#item-list").text()
        context = @model.attributes
        context.section_id = @options.section.id
        $(@el).html(template context)
        return this


class this.ItemListView extends Backbone.View
    render: =>
        @collection.each (item) =>
            @renderOne item
        return this

    renderOne: (item) =>
        view = new ItemView {model: item, section: @options.section}
        contents = view.render().el
        $(@el).append contents


class this.ItemDetailView extends Backbone.View
    tagName: "div"
    id: "itemDetail"

    events:
        "click #toggle-name": "toggleName"
        "click #toggle-extras": "toggleExtras"

    render: =>
        item = @model
        template = _.template $("#order-item").text()
        context = item.attributes
        context.section = @options.section
        context.choice_sets = item.choice_sets
        context.extras = item.extras
        context.prices = item.prices
        context.ordering = App.ordering
        $(@el).html(template context)
        @$('.extras').hide();
        return this

    toggleName: (e) =>
        nameTag = @$("#add-name")
        e.preventDefault()
        nameTag.show()

    toggleExtras: (e) ->
        extras = @$(".extras")
        targ = $(e.target)
        changeText = targ.data("text")
        currText = targ.text()
        e.preventDefault()
        targ.text(changeText).data "text", currText
        if extras.height()
            extras.hide()
                #anim {'height':'0px'}, .35, 'ease-in'
        else
            extras.show()
                #anim {'height':'auto'}, .35, 'ease-in'
