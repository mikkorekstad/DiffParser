from diffparser.parser import parse_diff

single_file_diff = "@@ -330,7 +330,7 @@ class DialsScaler(Scaler):\n           Debug.write('X1698: %s: %s' % (pointgroup, reindex_op))\n \n           if ntr:\n-            integrater.integrater_reset_reindex_operator()\n+            intgr.integrater_reset_reindex_operator()\n             need_to_return = True\n \n         if pt and not probably_twinned:\n"
print(parse_diff(single_file_diff, path_included=False))
