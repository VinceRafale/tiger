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

    events:
        "click input[type='submit']": "submitCoupon"
        "click #clear-coupon": "clearCoupon"

    initialize: ->
        @collection.bind "refresh", @render

    render: =>
        template = _.template $("#review-order").text()
        @el.innerHTML = template {
            subtotal: @collection.subtotal
            taxes: @collection.taxes
            total_plus_tax: @collection.total_plus_tax
            coupon: @collection.coupon
            discount: @collection.discount
        }

        @collection.each (section) =>
            @renderOne section

        return this

    renderOne: (line_item) =>
        view = new LineItemView {model: line_item}
        contents = view.render().el
        @$("tr.totals-first").before contents

    submitCoupon: (e) =>
        e.preventDefault()
        $.get "#{(@$ "form").attr "action"}?coupon_code=#{(@$ "input[type='text']").val()}", (data) =>
            newData = JSON.parse data
            if newData.error
                #TODO put data.msg somewhere and make it perty
                alert newData.msg
            else
                alert newData.msg
                [line_items, cart_data] = JSON.parse newData.cart
                App.cart.refreshCart line_items, cart_data

    clearCoupon: (e) =>
        e.preventDefault()
        $.get (($ e.target).attr "href"), (data) =>
            newData = JSON.parse data
            alert newData.msg
            [line_items, cart_data] = JSON.parse newData.cart
            App.cart.refreshCart line_items, cart_data
             

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
