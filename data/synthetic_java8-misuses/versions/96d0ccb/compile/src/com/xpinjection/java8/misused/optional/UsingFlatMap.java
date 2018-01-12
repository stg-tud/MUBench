package com.xpinjection.java8.misused.optional;

import static java.util.Optional.ofNullable;

import com.xpinjection.java8.misused.optional.HundredAndOneApproach.Car;
import com.xpinjection.java8.misused.optional.HundredAndOneApproach.Insurance;
import com.xpinjection.java8.misused.optional.HundredAndOneApproach.Person;

class UsingFlatMap {
    public String getCarInsuranceNameFromPersonUsingFlatMap(Person person) {
        return ofNullable(person)
                .flatMap(Person::getCar)
                .flatMap(Car::getInsurance)
                .map(Insurance::getName)
                .orElse("Unknown");
    }
}
