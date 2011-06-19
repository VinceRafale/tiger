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
        "click input[type='submit']": "addToCart"

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
        $(e.target).remove();
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
                 
    addToCart: =>
        #TODO: I wants spinny.  This shouldn't be a lengthy operation, but since everything
        # else in the menu takes just a few ms, it will seem long in comparison.
        # Zepto's missing "serialize", so we have to build a param object
        spinner =  App.spinner()
        spinnerContainer = @$ "input[type='submit']"
        cycle = setInterval (->
            spinnerContainer.val spinner()
        ), 300

        params = _.reduce (@$ "input,select,textarea").not("[type='submit'],[type='checkbox']"), ((memo, field) ->
            memo[($ field).attr "name"] = ($ field).val()
            return memo), {}
        checkboxes = _.reduce (@$  "[type='checkbox']"), ((memo, field) ->
            key = ($ field).attr "name"
            if ($ field).attr "checked"
                if memo[key]
                    memo[key].push ($ field).val()
                else
                    memo[key] = [($ field).val()]
            return memo), {}
        _.extend params, checkboxes

            
        $.post (@model.get "cart_url"), ($.param params, null, true), (data) =>
            newData = JSON.parse data
            clearInterval cycle
            spinner = null
            spinnerContainer.val "Add to order"
            if newData.error
                #TODO put data.msg somewhere and make it perty
                alert newData.msg
                if newData.fields
                    for field, err of newData.fields then do =>
                        input = (@$ "[name='#{field}']")
                        # Error is an array, because that's how Django rolls.  In practice
                        # there are virtually never multiple errors on one field, and we're
                        # going to count on that.
                        input.before "<span class='error'>#{err[0]}</span>"
            else
                [line_items, cart_data] = newData
                App.cart.refresh line_items, cart_data
                (@$ "span.error").remove()
                location.hash = (/#section\/\d+/.exec location.hash)[0]
                alert "#{@model.get "name"} successfully added to your order."
