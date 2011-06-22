class this.SectionView extends Backbone.View
    tagName: "li"

    render: =>
        template = _.template $("#section-list").text()
        context = @model.attributes
        $(@el).html template(context)
        return this


class this.SectionListView extends Backbone.View
    tagName: "ul"
    id: "sectionList"

    initialize: ->
        @collection.bind "add", @render

    render: =>
        $(@el).children().remove()

        @collection.each (section) =>
            @renderOne section

        return this

    renderOne: (section) =>
        view = new SectionView {model: section}
        contents = view.render().el
        $(@el).append contents


class this.SectionDetailView extends Backbone.View
    tagName: "div"
    id: "sectionDetail"

    render: =>
        template = _.template """<div class='breadcrumb'> <a href='/menu/'>Menu</a></div><h1><%= name %></h1><p><%= description %></p>
    <% if (schedule) { %>
    <p class="warning"><%= schedule %></p>
    <% } %><ul id='items'></ul>"""
        context = @model.attributes
        $(@el).html(template context)
        @itemList = new ItemListView {
            collection: @model.items
            el: @$("ul#items")
            section: @model
        }
        @itemList.render()
        return this
