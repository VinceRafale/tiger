// -------------------------------------------------------------------
// markItUp!
// -------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// -------------------------------------------------------------------
// MarkDown tags example
// http://en.wikipedia.org/wiki/Markdown
// http://daringfireball.net/projects/markdown/
// -------------------------------------------------------------------
// Feel free to add more tags
// -------------------------------------------------------------------
mySettings = {
	previewParserPath:	'',
	onShiftEnter:		{keepDefault:false, openWith:'\n\n'},
	markupSet: [
		{name:'First Level Heading', key:'1', placeHolder:'Your title here...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '=') } },
		{name:'Second Level Heading', key:'2', placeHolder:'Your title here...', closeWith:function(markItUp) { return miu.markdownTitle(markItUp, '-') } },
		{name:'Heading 3', key:'3', openWith:'### ', closeWith:' ###',  placeHolder:'Your title here...' },
		{name:'Bold', key:'B', openWith:'**', closeWith:'**'},
		{name:'Italic', key:'I', openWith:'_', closeWith:'_'},
		{name:'Bulleted List', replaceWith:function(markItUp) {return miu.markdownBullets(markItUp); } },
		{name:'Numeric List', replaceWith:function(markItUp) {return miu.markdownOrderedList(markItUp); }},
		{name:'Link', key:'L', openWith:'[', closeWith:']([![Url:!:http://]!] "[![Title]!]")', placeHolder:'Your text to link here...' },
		{name:'Quotes', openWith:'> '},
	]
}

// mIu nameSpace to avoid conflict.
miu = {
	markdownTitle: function(markItUp, char) {
		heading = '';
		n = $.trim(markItUp.selection||markItUp.placeHolder).length;
		for(i = 0; i < n; i++) {
			heading += char;
		}
		return '\n'+heading;
	},
    markdownBullets: function(markItUp) {
        lines = markItUp.selection.split(/\n/);
        items = [];
        for (i = 0; i < lines.length; i++) {
            if (lines[i] != '\n') items.push('- ' + lines[i]);
        }
        return items.join('\n');
    },
    markdownOrderedList: function(markItUp) {
        lines = markItUp.selection.split(/\n/);
        items = [];
        for (i = 0; i < lines.length; i++) {
            if (lines[i] != '\n') items.push((i + 1) + '. ' + lines[i]);
        }
        return items.join('\n');
    }
}
