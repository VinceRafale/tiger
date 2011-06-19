class CartSummaryView extends Backbone.View
    el: $ "div.cart"

    initialize: ->
        App.cart.bind "refresh", @render
        @render()

    render: =>
        if App.cart.size() > 0
            @el.html "<a class='button ordering' href='/menu/#review'>#{App.cart.size()} </a>"
        else
            @el.html """
            <div class="place-order">
            <span>Hungry?</span>
            <a class="button primary" href="/menu/#">Place an order</a>
            </div>
            """


class CartView extends Backbone.View
    tagName: "div"

    initialize: ->
        @collection.bind "refresh", @render

    render: =>
        template = _.template $("#review-order").text()
        @el.innerHTML = template {
            subtotal: @collection.subtotal
            taxes: @collection.taxes
            total_plus_tax: @collection.total_plus_tax
        }

        @collection.each (section) =>
            @renderOne section

        return this

    renderOne: (line_item) =>
        view = new LineItemView {model: line_item}
        contents = view.render().el
        @$("tr.taxes").before contents


class LineItemView extends Backbone.View
    tagName: "tr"

    events:
        "click a": "removeItem"

    render: =>
        template = _.template $("#line-item-template").text()
        context = @model.attributes
        _.extend context, {
            item: @model.item
            total: @model.total
            price: @model.price
        }
        $(@el).html(template context)
        return this

    removeItem: (e) =>
        e.preventDefault()
        target = $ e.target
        spinner =  App.spinner()
        cycle = setInterval (->
            target.html spinner()
        ), 300
        
        $.get (target.attr "href"), (data) =>
            clearInterval cycle
            spinner = null
            [line_items, cart_data] = JSON.parse data
            App.cart.refresh line_items, cart_data
