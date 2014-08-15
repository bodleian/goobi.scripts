<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:mods="http://www.loc.gov/mods/v3" exclude-result-prefixes="mods"
    xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:srw_dc="info:srw/schema/1/dc-schema"
    xmlns:oai_dc="oai_dc" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:odl="http://odl.ox.ac.uk/odl-mods-extensions/1.0/" xmlns:mets="http://www.loc.gov/METS/"
    xmlns:default="http://www.loc.gov/METS/" xmlns:dcterms="dcterms"
    xmlns:lookup="http://vocab.ox.ac.uk/lookup" xmlns:ox="ox" extension-element-prefixes="lookup"
    xmlns:goobi="http://goobi.bodleian.ox.ac.uk">
    <!-- version 0.1 of mods_to_dc_multi.xsl created by Yvonne Aburrow, 12-02-2013 -->
    <xsl:output method="xml" indent="yes" doctype-public="http://www.w3.org/2001/XMLSchema-instance"
        name="xml"/>
    <!--<xsl:variable name="outputDir" select="test"/>-->
    <xsl:param name="outputDir" required="yes"/>

    <xsl:template match="/">
        <xsl:choose>
            <!--if there is only one file, process its metadata without hasPart or isPartOf being inserted -->
            <xsl:when test="count(//mets:fileSec/mets:fileGrp)=1">
                <xsl:for-each select="//mods:mods">
                    <!-- get /mets:mets/mets:fileSec/mets:fileGrp/mets:file/@ID -->
                    <xsl:for-each select="/mets:mets/mets:fileSec/mets:fileGrp">
                        <xsl:for-each select="mets:file">
                            <xsl:variable name="numFileId" select="position()"/>
                            <xsl:variable name="actualFileId">
                                <xsl:choose>
                                    <xsl:when test="$numFileId &lt; 10">
                                        <xsl:text>-000</xsl:text>
                                        <xsl:value-of select="$numFileId"/>
                                    </xsl:when>
                                    <xsl:when
                                        test="($numFileId = 10) or (($numFileId &gt; 10) and ($numFileId &lt; 100))">
                                        <xsl:text>-00</xsl:text>
                                        <xsl:value-of select="$numFileId"/>
                                    </xsl:when>
                                    <xsl:when
                                        test="($numFileId = 100) or (($numFileId &gt; 100) and ($numFileId &lt; 1000))">
                                        <xsl:text>-0</xsl:text>
                                        <xsl:value-of select="$numFileId"/>
                                    </xsl:when>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:variable name="fileLabel"
                                select="concat(/mets:mets/mets:dmdSec[1]/mets:mdWrap[1]/mets:xmlData[1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='mods'][1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='extension'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='goobi'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='metadata'][6],$actualFileId)"/>
                            <xsl:variable name="location" select="concat($outputDir, $fileLabel)"/>
                            <xsl:variable name="filename" select="concat($location,'.xml')"/>
                            <xsl:value-of select="$filename"/>
                            <xsl:variable name="master" select="false()"/>
                            <!-- Creating  -->
                            <xsl:result-document href="{$filename}" format="xml">
                                <oai_dc:dc xmlns:dcterms1="http://purl.org/dc/terms/" xmlns:ox="ox"
                                    xmlns:dcterms="dcterms"
                                    xmlns:dc="http://purl.org/dc/elements/1.1/"
                                    xmlns:oai_dc="oai_dc"
                                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                    xsi:schemaLocation="oai_dc file:/Q:/itsd/Digital.Bodleian/schema/generated_dc.xsd">
                                    <xsl:call-template name="modsMods">
                                        <xsl:with-param name="count" select="1"/>
                                        <xsl:with-param name="master" select="$master"/>
                                        <xsl:with-param name="fileId" select="$fileLabel"/>
                                    </xsl:call-template>
                                </oai_dc:dc>
                            </xsl:result-document>
                        </xsl:for-each>
                    </xsl:for-each>
                </xsl:for-each>
            </xsl:when>
            <!--if there is more than one file, process metadata for each file -->
            <xsl:when test="count(//mets:fileSec/mets:fileGrp)>1">
                <xsl:for-each select="//mets:fileSec/mets:fileGrp">
                    <xsl:choose>
                        <!-- if it is the first iteration, create the parent document -->
                        <xsl:when test="position()=1">
                            <xsl:variable name="fileId"
                                select="number(substring(/mets:mets/mets:fileSec/mets:fileGrp/mets:file[1]/@ID,6,9))"/>
                            <xsl:variable name="actualFileId" select="$fileId+1"/>
                            <xsl:variable name="fileLabel"
                                select="concat(/mets:mets/mets:dmdSec[1]/mets:mdWrap[1]/mets:xmlData[1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='mods'][1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='extension'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='goobi'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='metadata'][6]/@name,$actualFileId)"/>

                            <xsl:variable name="location" select="concat($outputDir,$fileLabel)"/>
                            <xsl:variable name="filename" select="concat($location,'-master.xml')"/>
                            <xsl:variable name="master" select="true()"/>
                            <xsl:value-of select="$filename"/>
                            <!-- Creating  -->
                            <xsl:result-document href="{$filename}" format="xml">
                                <oai_dc:dc xmlns:dcterms1="http://purl.org/dc/terms/" xmlns:ox="ox"
                                    xmlns:dcterms="dcterms"
                                    xmlns:dc="http://purl.org/dc/elements/1.1/"
                                    xmlns:oai_dc="oai_dc"
                                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                    xsi:schemaLocation="oai_dc file:/Q:/itsd/Digital.Bodleian/schema/generated_dc.xsd">
                                    <xsl:for-each select="//mods:mods">
                                        <xsl:call-template name="modsMods">
                                            <xsl:with-param name="master" select="$master"/>
                                            <xsl:with-param name="fileId" select="$fileLabel"/>
                                        </xsl:call-template>
                                    </xsl:for-each>
                                    <xsl:for-each select="//mets:fileSec">
                                        <xsl:for-each
                                            select="/mets:mets/mets:fileSec/mets:fileGrp[1]/mets:file/mets:FLocat">
                                            <xsl:variable name="getfileid"
                                                select="tokenize(@xlink:href, '/')"/>
                                            <xsl:variable name="childFileId"
                                                select="substring-before(getfileid[last()],'.')"/>
                                            <dcterms:hasPart>
                                                <xsl:value-of select="$childFileId"/>
                                            </dcterms:hasPart>
                                        </xsl:for-each>
                                    </xsl:for-each>
                                </oai_dc:dc>
                            </xsl:result-document>
                        </xsl:when>
                        <!-- create the child documents -->
                        <xsl:otherwise>
                            <xsl:for-each select="/mets:mets/mets:fileSec/mets:fileGrp[1]">
                                <xsl:variable name="count" select="position()"/>
                                <xsl:variable name="master" select="false()"/>
                                <xsl:for-each select="mets:file">
                                    <xsl:variable name="fileId" select="number(substring(@ID,6,9))"/>
                                    <xsl:variable name="actualFileId" select="$fileId+1"/>
                                    <xsl:variable name="childFileLabel"
                                        select="concat(/mets:mets/mets:dmdSec[1]/mets:mdWrap[1]/mets:xmlData[1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='mods'][1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='extension'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='goobi'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='metadata'][6]/@name,$actualFileId)"/>

                                    <xsl:variable name="childLocation"
                                        select="concat($outputDir,$childFileLabel)"/>
                                    <xsl:variable name="childFilename"
                                        select="concat($childLocation,'.xml')"/>
                                    <xsl:value-of select="$childFilename"/>
                                    <!-- Creating  -->
                                    <xsl:result-document href="{$childFilename}" format="xml">
                                        <oai_dc:dc xmlns:dcterms1="http://purl.org/dc/terms/"
                                            xmlns:ox="ox" xmlns:dcterms="dcterms"
                                            xmlns:dc="http://purl.org/dc/elements/1.1/"
                                            xmlns:oai_dc="oai_dc"
                                            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                            xsi:schemaLocation="oai_dc file:/Q:/itsd/Digital.Bodleian/schema/generated_dc.xsd">
                                            <xsl:for-each select="//mods:mods">
                                                <xsl:call-template name="modsMods">
                                                  <xsl:with-param name="count" select="$count"/>
                                                  <xsl:with-param name="master" select="$master"/>
                                                </xsl:call-template>
                                            </xsl:for-each>
                                            <!--get parent doc title-->
                                            <xsl:for-each
                                                select="/mets:mets/mets:fileSec/mets:fileGrp[1]/mets:file">

                                                <xsl:variable name="masterFileId"
                                                  select="/mets:mets/mets:dmdSec[1]/mets:mdWrap[1]/mets:xmlData[1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='mods'][1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='extension'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='goobi'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='metadata'][6]/@name"/>

                                                <dcterms:isPartOf>
                                                  <xsl:value-of
                                                  select="concat($masterFileId,'-master')"/>
                                                </dcterms:isPartOf>
                                            </xsl:for-each>
                                        </oai_dc:dc>
                                    </xsl:result-document>
                                </xsl:for-each>
                            </xsl:for-each>
                        </xsl:otherwise>
                    </xsl:choose>
                    <!-- end of nested xsl:choose -->
                </xsl:for-each>
            </xsl:when>
        </xsl:choose>
    </xsl:template>
    <!--  MODS TEMPLATES -->
    <xsl:template name="modsMods">
        <xsl:param name="master" select="()"/>
        <xsl:param name="count" select="()"/>
        <xsl:param name="fileId" select="()"/>
        <xsl:for-each select="//mods:extension">
            <xsl:call-template name="modsExt">
                <xsl:with-param name="count" select="$count"/>
                <xsl:with-param name="master" select="$master"/>
                <xsl:with-param name="fileId" select="$fileId"/>
            </xsl:call-template>
        </xsl:for-each>
        <xsl:for-each select="//mods:titleInfo[@type='alternative']">
            <xsl:apply-templates select="."/>
        </xsl:for-each>
        <!-- apply all the other templates except mods:titleInfo, which has already been applied-->
        <xsl:apply-templates select="*[not(self::mods:titleInfo[1])]"/>
    </xsl:template>



    <xsl:template match="mods:extension" name="modsExt">
        <xsl:param name="count" select="()"/>
        <xsl:param name="master" select="()"/>
        <xsl:param name="fileId" select="()"/>
        <xsl:choose>
            <xsl:when test="$master=true()">
                <xsl:for-each
                    select="/default:mets/default:fileSec[1]/default:fileGrp[1]/default:file[1]/default:FLocat">
                    <dcterms:identifier type="ox:uuid">
                        <xsl:value-of
                            select="concat($fileId,'-master')"
                        />
                    </dcterms:identifier>
                    <dcterms:source type="ox:mediaId">
                        <xsl:value-of select="@ID[1]"/>
                    </dcterms:source>
                </xsl:for-each>
                <ox:sort>0</ox:sort>
            </xsl:when>
            <xsl:otherwise>
                <xsl:for-each
                    select="/default:mets/default:fileSec[1]/default:fileGrp[$count]/default:file[1]/default:FLocat">
                    <dcterms:identifier type="ox:uuid">
                        <xsl:value-of select="$fileId"/>
                    </dcterms:identifier>
                    <dcterms:source type="ox:mediaId">
                        <xsl:value-of select="@xlink:href"/>
                    </dcterms:source>
                </xsl:for-each>
                <ox:sort>
                    <xsl:value-of select="$count"/>
                </ox:sort>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:call-template name="goobi"/>
        <dcterms:type type="ox:risType">GEN</dcterms:type>
    </xsl:template>

    <!-- GOOBI-SPECIFIC TEMPLATES -->

    <xsl:template name="goobi">
        <xsl:for-each
            select="/mets:mets/mets:dmdSec/mets:mdWrap/mets:xmlData/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='mods']/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='extension']/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='goobi']/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='metadata']">
            <xsl:if test="@name='TitleDocMain'">
                <dcterms:title>
                    <xsl:value-of select="."/>
                </dcterms:title>
            </xsl:if>

            <xsl:if test="@name='TitleDocMainShort'">
                <dcterms:alternative>
                    <xsl:value-of select="."/>
                </dcterms:alternative>
            </xsl:if>

            <xsl:if test="@name='Bearbeiter'">
                <xsl:for-each select="goobi:displayName">
                    <xsl:if test="not(contains(.,','))">
                        <dcterms:contributor>
                            <xsl:value-of select="."/>
                            <xsl:text> (editor)</xsl:text>
                        </dcterms:contributor>
                    </xsl:if>
                </xsl:for-each>
            </xsl:if>

            <xsl:if test="@name='Editor'">
                <xsl:for-each select="goobi:displayName">
                    <xsl:if test="not(contains(.,','))">
                        <dcterms:contributor>
                            <xsl:value-of select="."/>
                            <xsl:text> (editor)</xsl:text>
                        </dcterms:contributor>
                    </xsl:if>
                </xsl:for-each>
            </xsl:if>

            <xsl:if test="@name='Composer'">
                <xsl:for-each select="goobi:displayName">
                    <xsl:if test="not(contains(.,','))">
                        <dcterms:creator>
                            <xsl:value-of select="."/>
                            <xsl:text> (composer)</xsl:text>
                        </dcterms:creator>
                    </xsl:if>
                </xsl:for-each>
            </xsl:if>

            <xsl:if test="@name='Author'">
                <xsl:for-each select="goobi:displayName">
                    <xsl:if test="not(contains(.,','))">
                        <dcterms:author>
                            <xsl:value-of select="normalize-space(substring-after(.,','))"/>
                            <xsl:text> </xsl:text>
                            <xsl:value-of select="normalize-space(substring-before(.,','))"/>
                        </dcterms:author>
                    </xsl:if>
                </xsl:for-each>
            </xsl:if>

            <xsl:if test="@name='pathimagefiles'">
                <dcterms:source>
                    <xsl:value-of select="."/>
                </dcterms:source>
            </xsl:if>

            <xsl:if test="@name='shelfmarksource'">
                <dcterms:identifier type="ox:shelfmark">
                    <xsl:value-of select="."/>
                </dcterms:identifier>
            </xsl:if>

            <xsl:if test="@name='CatalogueIDSource'">
                <dcterms:identifier type="ox:shelfmark">
                    <xsl:value-of select="."/>
                </dcterms:identifier>
            </xsl:if>

            <xsl:if test="@name='CatalogueIDDigital'">
                <dcterms:identifier type="ox:uuid">
                    <xsl:value-of select="."/>
                </dcterms:identifier>
            </xsl:if>

            <xsl:if test="@name='PublicationYear'">
                <dcterms:date>
                    <xsl:value-of select="."/>
                </dcterms:date>
            </xsl:if>

            <xsl:if test="@name='singleDigCollection'">
                <dcterms:format>
                    <xsl:value-of select="."/>
                </dcterms:format>
            </xsl:if>

            <xsl:if test="@name='DocLanguage'">
                <ox:displayLanguage>
                    <xsl:value-of select="."/>
                </ox:displayLanguage>

                <xsl:if test=".='Afar'">
                    <dcterms:language>aar</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Abkhazian'">
                    <dcterms:language>abk</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Achinese'">
                    <dcterms:language>ace</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Acoli'">
                    <dcterms:language>ach</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Adangme'">
                    <dcterms:language>ada</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Afro-Asiatic (Other)'">
                    <dcterms:language>afa</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Afrihili'">
                    <dcterms:language>afh</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Africaans'">
                    <dcterms:language>afr</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Aljamia'">
                    <dcterms:language>ajm</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Akan'">
                    <dcterms:language>aka</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Akkadian'">
                    <dcterms:language>akk</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Albanian'">
                    <dcterms:language>alb</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Aleut'">
                    <dcterms:language>ale</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Algonquian languages'">
                    <dcterms:language>alg</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Amharic'">
                    <dcterms:language>amh</dcterms:language>
                </xsl:if>
                <xsl:if test=".='English, Old (ca. 450-1100)'">
                    <dcterms:language>ang</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Apache languages'">
                    <dcterms:language>apa</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Arabic'">
                    <dcterms:language>ara</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Aramaic'">
                    <dcterms:language>arc</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Armenian'">
                    <dcterms:language>arm</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Araucanian'">
                    <dcterms:language>arn</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Arapaho'">
                    <dcterms:language>arp</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Artificial (Other)'">
                    <dcterms:language>art</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Arawak'">
                    <dcterms:language>arw</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Assamese'">
                    <dcterms:language>asm</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Athapascan languages'">
                    <dcterms:language>ath</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Avaric'">
                    <dcterms:language>ava</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Avestan'">
                    <dcterms:language>ave</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Awandhi'">
                    <dcterms:language>awa</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Aymara'">
                    <dcterms:language>aym</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Azerbaijani'">
                    <dcterms:language>aze</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Banda'">
                    <dcterms:language>bad</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Bamileke languages'">
                    <dcterms:language>bai</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Bashkir'">
                    <dcterms:language>bak</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Baluchi'">
                    <dcterms:language>bal</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Bambara'">
                    <dcterms:language>bam</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Balinese'">
                    <dcterms:language>ban</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Basque'">
                    <dcterms:language>baq</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Basa'">
                    <dcterms:language>bas</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Baltic (Other)'">
                    <dcterms:language>bat</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Beja'">
                    <dcterms:language>bej</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Byelorussian'">
                    <dcterms:language>bel</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Bemba'">
                    <dcterms:language>bem</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Bengali'">
                    <dcterms:language>ben</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Berber languages'">
                    <dcterms:language>ber</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Bhojpuri'">
                    <dcterms:language>bho</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Bihari'">
                    <dcterms:language>bih</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Bikol'">
                    <dcterms:language>bik</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Bini'">
                    <dcterms:language>bin</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Bislama'">
                    <dcterms:language>bis</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Siksika'">
                    <dcterms:language>bla</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tibetan'">
                    <dcterms:language>bod/tib</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Braj'">
                    <dcterms:language>bra</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Breton'">
                    <dcterms:language>bre</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Buginese'">
                    <dcterms:language>bug</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Bulgarian'">
                    <dcterms:language>bul</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Burmese'">
                    <dcterms:language>bur</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Caddo'">
                    <dcterms:language>cad</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Central American Indian (Other)'">
                    <dcterms:language>cai</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Carib'">
                    <dcterms:language>car</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Catalan'">
                    <dcterms:language>cat</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Caucasian (Other)'">
                    <dcterms:language>cau</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Cebuano'">
                    <dcterms:language>ceb</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Celtic (Other)'">
                    <dcterms:language>cel</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Czeck'">
                    <dcterms:language>ces</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Chamorro'">
                    <dcterms:language>cha</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Chibcha'">
                    <dcterms:language>chb</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Chechen'">
                    <dcterms:language>che</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Chagatai'">
                    <dcterms:language>chg</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Chinese'">
                    <dcterms:language>chi</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Chinook jargon'">
                    <dcterms:language>chn</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Choctaw'">
                    <dcterms:language>cho</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Cherokee'">
                    <dcterms:language>chr</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Church Slavic'">
                    <dcterms:language>chu</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Chuvash'">
                    <dcterms:language>chv</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Cheyenne'">
                    <dcterms:language>chy</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Coptic'">
                    <dcterms:language>cop</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Cornish'">
                    <dcterms:language>cor</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Corsican'">
                    <dcterms:language>cos</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Creoles and pidgins, English-based (Other)'">
                    <dcterms:language>cpe</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Creoles and pidgins, French-based (Other)'">
                    <dcterms:language>cpf</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Creoles and pidgins, Portuguese-based (Other)'">
                    <dcterms:language>cpp</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Cree'">
                    <dcterms:language>cre</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Creoles and pidgins (Other)'">
                    <dcterms:language>crp</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Cushitic (Other)'">
                    <dcterms:language>cus</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Welsh'">
                    <dcterms:language>wel</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Czech'">
                    <dcterms:language>cze</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Dakota'">
                    <dcterms:language>dak</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Danish'">
                    <dcterms:language>dan</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Delaware'">
                    <dcterms:language>del</dcterms:language>
                </xsl:if>
                <xsl:if test=".='German'">
                    <dcterms:language>ger</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Dinka'">
                    <dcterms:language>din</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Dogri'">
                    <dcterms:language>doi</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Dravidian (Other)'">
                    <dcterms:language>dra</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Duala'">
                    <dcterms:language>dua</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Dutch, Middle (ca. 1050-1350)'">
                    <dcterms:language>dum</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Dutch'">
                    <dcterms:language>dut</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Dyula'">
                    <dcterms:language>dyu</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Dzongkha'">
                    <dcterms:language>dzo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Efik'">
                    <dcterms:language>efi</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Egyptian (Ancient)'">
                    <dcterms:language>egy</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ekajuk'">
                    <dcterms:language>eka</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Greek, Modern (1453- )'">
                    <dcterms:language>gre</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Elamite'">
                    <dcterms:language>elx</dcterms:language>
                </xsl:if>
                <xsl:if test=".='English'">
                    <dcterms:language>eng</dcterms:language>
                </xsl:if>
                <xsl:if test=".='English, Middle (1100-1500)'">
                    <dcterms:language>enm</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Esperanto'">
                    <dcterms:language>epo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Eskimo (Other)'">
                    <dcterms:language>esk</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Spanish'">
                    <dcterms:language>esl/spa</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Estonian'">
                    <dcterms:language>est</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ethiopic'">
                    <dcterms:language>eth</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Basque'">
                    <dcterms:language>baq</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ewe'">
                    <dcterms:language>ewe</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ewondo'">
                    <dcterms:language>ewo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Fang'">
                    <dcterms:language>fan</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Faroese'">
                    <dcterms:language>fao</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Persian'">
                    <dcterms:language>per</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Fanti'">
                    <dcterms:language>fat</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Fijian'">
                    <dcterms:language>fij</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Finnish'">
                    <dcterms:language>fin</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Finno-Ugrian (Other)'">
                    <dcterms:language>fiu</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Fon'">
                    <dcterms:language>fon</dcterms:language>
                </xsl:if>
                <xsl:if test=".='French'">
                    <dcterms:language>fre</dcterms:language>
                </xsl:if>
                <xsl:if test=".='French, Middle (ca. 1400-1600)'">
                    <dcterms:language>frm</dcterms:language>
                </xsl:if>
                <xsl:if test=".='French, Old (ca. 842-1400)'">
                    <dcterms:language>fro</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Friesian'">
                    <dcterms:language>fry</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Fulah'">
                    <dcterms:language>ful</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ga'">
                    <dcterms:language>gaa</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Gaelic (Scots)'">
                    <dcterms:language>gae</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Irish'">
                    <dcterms:language>iri</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Gayo'">
                    <dcterms:language>gay</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Germanic (Other)'">
                    <dcterms:language>gem</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Georgian'">
                    <dcterms:language>geo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Gilbertese'">
                    <dcterms:language>gil</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Gallegan'">
                    <dcterms:language>glg</dcterms:language>
                </xsl:if>
                <xsl:if test=".='German, Middle High (ca. 1050-1500)'">
                    <dcterms:language>gmh</dcterms:language>
                </xsl:if>
                <xsl:if test=".='German, Old High (ca. 750-1050)'">
                    <dcterms:language>goh</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Gondi'">
                    <dcterms:language>gon</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Gothic'">
                    <dcterms:language>got</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Grebo'">
                    <dcterms:language>grb</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Greek, Ancient (to 1453)'">
                    <dcterms:language>grc</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Greek, Modern (1453- )'">
                    <dcterms:language>gre/ell</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Guarani'">
                    <dcterms:language>grn</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Gujarati'">
                    <dcterms:language>guj</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Haida'">
                    <dcterms:language>hai</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Hausa'">
                    <dcterms:language>hau</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Hawaiian'">
                    <dcterms:language>haw</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Hebrew'">
                    <dcterms:language>heb</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Herero'">
                    <dcterms:language>her</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Hiligaynon'">
                    <dcterms:language>hil</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Himachali'">
                    <dcterms:language>him</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Hindi'">
                    <dcterms:language>hin</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Hiri Motu'">
                    <dcterms:language>hmo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Hungarian'">
                    <dcterms:language>hun</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Hupa'">
                    <dcterms:language>hup</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Iban'">
                    <dcterms:language>iba</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Igbo'">
                    <dcterms:language>ibo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Icelandic'">
                    <dcterms:language>ice</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ijo'">
                    <dcterms:language>ijo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Inuktitut'">
                    <dcterms:language>iku</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Interlingue'">
                    <dcterms:language>ile</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Iloko'">
                    <dcterms:language>ilo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Indic (Other)'">
                    <dcterms:language>inc</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Indonesian'">
                    <dcterms:language>ind</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Indo-European (Other)'">
                    <dcterms:language>ine</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Inupiak'">
                    <dcterms:language>ipk</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Iranian (Other)'">
                    <dcterms:language>ira</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Irish'">
                    <dcterms:language>iri/gai</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Iroquoian languages'">
                    <dcterms:language>iro</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Italian'">
                    <dcterms:language>ita</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Javanese'">
                    <dcterms:language>jav</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Japanese'">
                    <dcterms:language>jpn</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Judeo-Persian'">
                    <dcterms:language>jpr</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Judeo-Arabic'">
                    <dcterms:language>jrb</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kara-Kalpak'">
                    <dcterms:language>kaa</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kabyle'">
                    <dcterms:language>kab</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kachin'">
                    <dcterms:language>kac</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Greenlandic'">
                    <dcterms:language>kal</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kamba'">
                    <dcterms:language>kam</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kannada'">
                    <dcterms:language>kan</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Karen'">
                    <dcterms:language>kar</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kashmiri'">
                    <dcterms:language>kas</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Georgian'">
                    <dcterms:language>kat/geo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kanuri'">
                    <dcterms:language>kau</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kawi'">
                    <dcterms:language>kaw</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kazakh'">
                    <dcterms:language>kaz</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Khasi'">
                    <dcterms:language>kha</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Khoisan (Other)'">
                    <dcterms:language>khi</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Khmer'">
                    <dcterms:language>khm</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Khotanese'">
                    <dcterms:language>kho</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kikuyu'">
                    <dcterms:language>kik</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kinyarwanda'">
                    <dcterms:language>kin</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kirghiz'">
                    <dcterms:language>kir</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Konkani'">
                    <dcterms:language>kok</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kongo'">
                    <dcterms:language>kon</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Korean'">
                    <dcterms:language>kor</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kpelle'">
                    <dcterms:language>kpe</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kru'">
                    <dcterms:language>kro</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kurukh'">
                    <dcterms:language>kru</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kuanyama'">
                    <dcterms:language>kua</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kurdish'">
                    <dcterms:language>kur</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kusaie'">
                    <dcterms:language>kus</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Kutenai'">
                    <dcterms:language>kut</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ladino'">
                    <dcterms:language>lad</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Lahnda'">
                    <dcterms:language>lah</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Lamba'">
                    <dcterms:language>lam</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Lao'">
                    <dcterms:language>lao</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Lapp languages'">
                    <dcterms:language>lap</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Latin'">
                    <dcterms:language>lat</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Latvian'">
                    <dcterms:language>lav</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Lingala'">
                    <dcterms:language>lin</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Lithuanian'">
                    <dcterms:language>lit</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Mongo'">
                    <dcterms:language>lol</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Lozi'">
                    <dcterms:language>loz</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Luba-Katanga'">
                    <dcterms:language>lub</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ganda'">
                    <dcterms:language>lug</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Luiseno'">
                    <dcterms:language>lui</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Lunda'">
                    <dcterms:language>lun</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Luo (Kenya and Tanzania)'">
                    <dcterms:language>luo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Macedonian'">
                    <dcterms:language>mac/mke</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Madurese'">
                    <dcterms:language>mad</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Magahi'">
                    <dcterms:language>mag</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Marshall'">
                    <dcterms:language>mah</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Maithili'">
                    <dcterms:language>mai</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Makasar'">
                    <dcterms:language>mak</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Malayalam'">
                    <dcterms:language>mal</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Mandingo'">
                    <dcterms:language>man</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Maori'">
                    <dcterms:language>mao</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Austronesian (Other)'">
                    <dcterms:language>map</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Marathi'">
                    <dcterms:language>mar</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Masai'">
                    <dcterms:language>mas</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Manx'">
                    <dcterms:language>max</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Malay'">
                    <dcterms:language>may</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Mende'">
                    <dcterms:language>men</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Micmac'">
                    <dcterms:language>mic</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Minangkabau'">
                    <dcterms:language>min</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Miscellaneous (Other)'">
                    <dcterms:language>mis</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Macedonian'">
                    <dcterms:language>mac</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Mon-Khmer (Other)'">
                    <dcterms:language>mkh</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Malagasy'">
                    <dcterms:language>mlg</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Maltese'">
                    <dcterms:language>mlt</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Manipuri'">
                    <dcterms:language>mni</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Manobo languages'">
                    <dcterms:language>mno</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Mohawk'">
                    <dcterms:language>moh</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Moldavian'">
                    <dcterms:language>mol</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Mongolian'">
                    <dcterms:language>mon</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Mossi'">
                    <dcterms:language>mos</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Multiple languages'">
                    <dcterms:language>mul</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Munda (Other)'">
                    <dcterms:language>mun</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Creek'">
                    <dcterms:language>mus</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Marwari'">
                    <dcterms:language>mwr</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Mayan languages'">
                    <dcterms:language>myn</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Aztec'">
                    <dcterms:language>nah</dcterms:language>
                </xsl:if>
                <xsl:if test=".='North American Indian (Other)'">
                    <dcterms:language>nai</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Nauru'">
                    <dcterms:language>nau</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Navajo'">
                    <dcterms:language>nav</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ndebele (Zimbabwe)'">
                    <dcterms:language>nde</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ndonga'">
                    <dcterms:language>ndo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Nepali'">
                    <dcterms:language>nep</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Newari'">
                    <dcterms:language>new</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Niger-Kordofanian (Other)'">
                    <dcterms:language>nic</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Niuean'">
                    <dcterms:language>niu</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Dutch'">
                    <dcterms:language>nld/dut</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Old Norse'">
                    <dcterms:language>non</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Norwegian'">
                    <dcterms:language>nor</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Northern Sohto'">
                    <dcterms:language>nso</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Nubian languages'">
                    <dcterms:language>nub</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Nyanja'">
                    <dcterms:language>nya</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Nyamwezi'">
                    <dcterms:language>nym</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Nyankole'">
                    <dcterms:language>nyn</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Nyoro'">
                    <dcterms:language>nyo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Nzima'">
                    <dcterms:language>nzi</dcterms:language>
                </xsl:if>
                <xsl:if test="contains(.,'Langue')">
                    <dcterms:language>oci</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ojibwa'">
                    <dcterms:language>oji</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Oriya'">
                    <dcterms:language>ori</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Oromo'">
                    <dcterms:language>orm</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Osage'">
                    <dcterms:language>osa</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ossetic'">
                    <dcterms:language>oss</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Turkish, Ottoman'">
                    <dcterms:language>ota</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Otomian languages'">
                    <dcterms:language>oto</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Papuan-Australian (Other)'">
                    <dcterms:language>paa</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Pangasinan'">
                    <dcterms:language>pag</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Pahlavi'">
                    <dcterms:language>pal</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Pampanga'">
                    <dcterms:language>pam</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Panjabi'">
                    <dcterms:language>pan</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Papiamento'">
                    <dcterms:language>pap</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Palauan'">
                    <dcterms:language>pau</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Old Persian (ca. 600-400 B.C.)'">
                    <dcterms:language>peo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Pali'">
                    <dcterms:language>pli</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Polish'">
                    <dcterms:language>pol</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ponape'">
                    <dcterms:language>pon</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Portuguese'">
                    <dcterms:language>por</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Prakrit languages'">
                    <dcterms:language>pra</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Provencal, Old (to 1500)'">
                    <dcterms:language>pro</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Pushto'">
                    <dcterms:language>pus</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Quechua'">
                    <dcterms:language>que</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Rajasthani'">
                    <dcterms:language>raj</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Rarotongan'">
                    <dcterms:language>rar</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Romance (Other)'">
                    <dcterms:language>roa</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Raeto-Romance'">
                    <dcterms:language>roh</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Romany'">
                    <dcterms:language>rom</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Romanian'">
                    <dcterms:language>ron/rum</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Romanian'">
                    <dcterms:language>rum/ron</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Rundi'">
                    <dcterms:language>run</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Russian'">
                    <dcterms:language>rus</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sandawe'">
                    <dcterms:language>sad</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sango'">
                    <dcterms:language>sag</dcterms:language>
                </xsl:if>
                <xsl:if test=".='South American Indian (Other)'">
                    <dcterms:language>sai</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Salishan languages'">
                    <dcterms:language>sal</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Samaritan Aramaic'">
                    <dcterms:language>sam</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sanskrit'">
                    <dcterms:language>san</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Scots'">
                    <dcterms:language>sco</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Serbo-Croatian'">
                    <dcterms:language>scr</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Selkup'">
                    <dcterms:language>sel</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Semitic (Other)'">
                    <dcterms:language>sem</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Shan'">
                    <dcterms:language>shn</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sidamo'">
                    <dcterms:language>sid</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sinhalese'">
                    <dcterms:language>sin</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Siouan languages'">
                    <dcterms:language>sio</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sino-Tibetan (Other)'">
                    <dcterms:language>sit</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Slavic (Other)'">
                    <dcterms:language>sla</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Slovak'">
                    <dcterms:language>slk/slo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Slovak'">
                    <dcterms:language>slo/slk</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Slovenian'">
                    <dcterms:language>slv</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Samoan'">
                    <dcterms:language>smo</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Shona'">
                    <dcterms:language>sna</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sindhi'">
                    <dcterms:language>snd</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sogdian'">
                    <dcterms:language>sog</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Somali'">
                    <dcterms:language>som</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Songhai'">
                    <dcterms:language>son</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sotho'">
                    <dcterms:language>sot</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Spanish'">
                    <dcterms:language>spa/esl</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Albanian'">
                    <dcterms:language>sqi/alb</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Serer'">
                    <dcterms:language>srr</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Nilo-Saharan (Other)'">
                    <dcterms:language>ssa</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Swazi'">
                    <dcterms:language>ssw</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sukuma'">
                    <dcterms:language>suk</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sundanese'">
                    <dcterms:language>sun</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Susu'">
                    <dcterms:language>sus</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sumerian'">
                    <dcterms:language>sux</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Swedish'">
                    <dcterms:language>sve/swe</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Swahili'">
                    <dcterms:language>swa</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Swedish'">
                    <dcterms:language>swe/sve</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Syriac'">
                    <dcterms:language>syr</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tahitian'">
                    <dcterms:language>tah</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tamil'">
                    <dcterms:language>tam</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tatar'">
                    <dcterms:language>tat</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Telugu'">
                    <dcterms:language>tel</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Timne'">
                    <dcterms:language>tem</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tereno'">
                    <dcterms:language>ter</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tajik'">
                    <dcterms:language>tgk</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tagalog'">
                    <dcterms:language>tgl</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Thai'">
                    <dcterms:language>tha</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tibetan'">
                    <dcterms:language>tib</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tigre'">
                    <dcterms:language>tig</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tigrinya'">
                    <dcterms:language>tir</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tivi'">
                    <dcterms:language>tiv</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tlingit'">
                    <dcterms:language>tli</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tonga (Nyasa)'">
                    <dcterms:language>tog</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tonga (Tonga Islands)'">
                    <dcterms:language>ton</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Truk'">
                    <dcterms:language>tru</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tsimshian'">
                    <dcterms:language>tsi</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tswana'">
                    <dcterms:language>tsn</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tsonga'">
                    <dcterms:language>tso</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Turkmen'">
                    <dcterms:language>tuk</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Tumbuka'">
                    <dcterms:language>tum</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Turkish'">
                    <dcterms:language>tur</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Altaic (Other)'">
                    <dcterms:language>tut</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Twi'">
                    <dcterms:language>twi</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ugaritic'">
                    <dcterms:language>uga</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Uighur'">
                    <dcterms:language>uig</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Ukrainian'">
                    <dcterms:language>ukr</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Umbundu'">
                    <dcterms:language>umb</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Undetermined'">
                    <dcterms:language>und</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Urdu'">
                    <dcterms:language>urd</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Uzbek'">
                    <dcterms:language>uzb</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Vai'">
                    <dcterms:language>vai</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Venda'">
                    <dcterms:language>ven</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Vietnamese'">
                    <dcterms:language>vie</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Volapuk'">
                    <dcterms:language>vol</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Votic'">
                    <dcterms:language>vot</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Wakashan languages'">
                    <dcterms:language>wak</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Walamo'">
                    <dcterms:language>wal</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Waray'">
                    <dcterms:language>war</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Washo'">
                    <dcterms:language>was</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Sorbian languages'">
                    <dcterms:language>wen</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Wolof'">
                    <dcterms:language>wol</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Xhosa'">
                    <dcterms:language>xho</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Yao'">
                    <dcterms:language>yao</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Yap'">
                    <dcterms:language>yap</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Yiddish'">
                    <dcterms:language>yid</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Yoruba'">
                    <dcterms:language>yor</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Zapotec'">
                    <dcterms:language>zap</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Zenaga'">
                    <dcterms:language>zen</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Zhuang'">
                    <dcterms:language>zha</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Zulu'">
                    <dcterms:language>zul</dcterms:language>
                </xsl:if>
                <xsl:if test=".='Zuni'">
                    <dcterms:language>zun</dcterms:language>
                </xsl:if>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
