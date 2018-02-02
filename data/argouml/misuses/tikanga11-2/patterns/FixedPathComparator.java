import java.text.Collator;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;

import org.argouml.model.Model;

class FixedPathComparator {
  private Collator collator;
  
    int comparePaths(Object o1, Object o2) {
        List<String> path1 = 
            Model.getModelManagementHelper().getPathList(o1);
        Collections.reverse(path1);
        List<String> path2 = 
            Model.getModelManagementHelper().getPathList(o2);
        Collections.reverse(path2);
        
        Iterator<String> i2 = path2.iterator();
        Iterator<String> i1 = path1.iterator();
        int caseSensitiveComparison = 0;
        while (i2.hasNext()) {
            String name2 = i2.next();
            if (!i1.hasNext()) {
                return -1;
            }
            String name1 = i1.next();
            int comparison;
            if (name1 == null) {
                if (name2 == null) {
                    comparison = 0; 
                } else {
                    comparison = -1;
                }
            } else if (name2 == null) {
                comparison = 1;
            } else {
                comparison = collator.compare(name1, name2);
            }
            if (comparison != 0) {
                return comparison;
            }
            // Keep track of first non-equal comparison to use in case the
            // case-insensitive comparisons all end up equal
            if (caseSensitiveComparison == 0) {
                if (name1 == null) {
                    if (name2 == null) {
                        caseSensitiveComparison = 0;
                    } else {
                        caseSensitiveComparison = -1;
                    }
                } else if (name2 == null) {
                    caseSensitiveComparison = 1;
                } else {
                    caseSensitiveComparison = name1.compareTo(name2);
                }
            }
        }
        if (i2.hasNext()) {
            return 1;
        }
        // If the strings differed only in non-primary characteristics at
        // some point (case, accent, etc) pick an arbitrary, but stable, 
        // collating order.
        if (caseSensitiveComparison != 0) {
            return caseSensitiveComparison;
        }
        // It's illegal in UML to have multiple elements in a namespace with
        // the same name, but if it happens, keep them distinct so the user
        // has a chance of catching the error.  Pick an arbitrary, but stable,
        // collating order.
        // We don't call them equal because otherwise one will get eliminated
        // from the TreeSet where this comparator is used.
        return o1.toString().compareTo(o2.toString());
    }
}
