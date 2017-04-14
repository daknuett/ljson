modname=ljson

github:
	sed -i -- 's/_static/static/g'   *.html
	sed -i -- 's/_sources/sources/g'   *.html
	sed -i -- 's/_images/images/g'   *.html
	sed -i -- 's/_modules/modules/g' *.html
	if [ -e  _modules/ ] ; then sed -i -- 's/_static/static/g'   _modules/$(modname)/*/*.html; fi
	if [ -e  _modules/ ] ; then sed -i -- 's/_images/images/g'   _modules/$(modname)/*/*.html; fi
	if [ -e  _modules/ ] ; then sed -i -- 's/_modules/modules/g' _modules/$(modname)/*/*.html; fi
	if [ -e  _static/ ] ; then mv _static/ ./static/; fi
	if [ -e  _sources/ ] ; then mv _sources/ ./sources/; fi
	if [ -e  _images/ ] ; then mv _images/ ./images/; fi
	if [ -e  _modules/ ] ; then mv _modules/ ./modules/; fi

