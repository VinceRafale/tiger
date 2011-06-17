class CartView extends Backbone.View
    tagName: "div"

    initialize: ->
        @collection.bind "remove", @render

    render: =>
        template = _.template $("#review-order").text()
        @el.innerHTML = template {}

        @collection.each (section) =>
            @renderOne section

        return this

    renderOne: (line_item) =>
        view = new LineItemView {model: line_item}
        contents = view.render().el
        @$("table").append contents


class LineItemView extends Backbone.View
    tagName: "tr"

    render: =>
        template = _.template $("#line-item-template").text()
        context = @model.attributes
        _.extend context, {
            price: @model.price
            extras: @model.extras
            choices: @model.choices
            item: @model.item
            total: @model.total
        }
        console.log @model.price
        $(@el).html(template context)
        return this
