import org.aspectj.weaver.bcel.BcelClassWeaver;RightIter.java

class RightIter extends BcelClassWeaver {
  boolean pattern(List decaMCs, List itdMethodsCtors,List reportedErrors) {
    boolean isChanged = false;
    BcelTypeMunger fieldMunger = (BcelTypeMunger) iter.next();
    ResolvedMember itdIsActually = fieldMunger.getSignature();
    List worthRetrying = new ArrayList();
    boolean modificationOccured = false;
    while (!worthRetrying.isEmpty() && modificationOccured) {
        modificationOccured = false;
                List forRemoval = new ArrayList();
                for (Iterator iter2 = worthRetrying.iterator(); iter2.hasNext();) {
          DeclareAnnotation decaF = (DeclareAnnotation) iter2.next();
          if (decaF.matches(itdIsActually,world)) {
          LazyMethodGen annotationHolder = locateAnnotationHolderForFieldMunger(clazz,fieldMunger);
          if (doesAlreadyHaveAnnotation(annotationHolder,itdIsActually,decaF,reportedErrors)) continue; // skip this one...
          annotationHolder.addAnnotation(decaF.getAnnotationX());
          AsmRelationshipProvider.getDefault().addDeclareAnnotationRelationship(decaF.getSourceLocation(),itdIsActually.getSourceLocation());
          isChanged = true;
          modificationOccured = true;
          forRemoval.add(decaF);
          }
          worthRetrying.removeAll(forRemoval);
                }
        }
    }
    return isChanged;
  }
}
