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
        params = _.reduce (@$ "input,select,textarea").not("[type='submit']"), ((memo, field) ->
            memo[($ field).attr "name"] = ($ field).val()
            return memo), {}
            
        $.post (@model.get "cart_url"), ($.param params), (data) =>
            if data.error
                #TODO put data.msg somewhere and make it perty
                console.log data
            else
                #TODO beautify this
                alert "#{@model.get "name"} successfully added to your order."
                App.cart.refresh (JSON.parse data)
            
