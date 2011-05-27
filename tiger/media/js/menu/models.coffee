class this.Section extends Backbone.Model
    initialize: ->
        @items = new Items(@get "items")


class this.Sections extends Backbone.Collection
    model: Section

    comparator: (section) ->
        return section.id

class this.Item extends Backbone.Model
    initialize: ->
        @extras = new Extras(@get "extras")
        @prices = new Variants(@get "prices")
        @choice_sets = new ChoiceSets(@get "choices")


class this.Items extends Backbone.Collection
    model: Item

    comparator: (item) ->
       return item.id


class this.Variant extends Backbone.Model


class this.Variants extends Backbone.Collection
    model: Variant


class this.Extra extends Backbone.Model


class this.Extras extends Backbone.Collection
    model: Extra


class this.ChoiceSet extends Backbone.Model
    initialize: ->
        @choices = new Choices(@get "sidedishes")


class this.ChoiceSets extends Backbone.Collection
    model: ChoiceSet


class this.Choice extends Backbone.Model


class this.Choices extends Backbone.Collection
    model: Choice
